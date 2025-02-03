import random
from tempfile import template
from flask import Blueprint, render_template, request, jsonify
from database import BoxTemporalSeries, db, Assignment, Box, Tool, Operator
from sqlalchemy import delete, select, update

TEMPORAL_SERIE_WINDOW = 5

TEMPERATURE_RANGE = 20
HUMIDITY_ALLOWANCE = 10
ACCELERATION_ALLOWANCE = 25
WEIGHT_ALLOWANCE = 3000

index = Blueprint('index', __name__)


def jsonify_results(results):
    return jsonify([result[0].to_dict() for result in results])

# When requested returns the home screen of the dashboard
@index.route('/')
def home():
    id_and_name_query = select(Box.id, Operator.name).join_from(Box, Operator)
    ids_and_names_list = db.session.execute(id_and_name_query).all()

    boxList = []

    for tuple in ids_and_names_list:
        boxList.append({
            'id': tuple[0],
            'operator': tuple[1]
        })
    return render_template('home.html', boxList = boxList)

# When requested returns the tools screen of the dashboard
@index.route('/tools')
def toolsDashboard():
    boxes_query = select(Box.id)
    ids_list = db.session.execute(boxes_query).all()

    unique_boxes = []

    for id in ids_list:
        unique_boxes.append(id[0])

    tools_query = select(Tool.name, Assignment.id_box).join_from(Tool, Assignment)
    tools_list = db.session.execute(tools_query).all()
    tools = []

    for tuple in tools_list:
        tools.append({
            'name': tuple[0],
            'box': tuple[1]
        })

    return render_template('tools.html', objects = tools, unique_boxes = unique_boxes)

# When requested returns the boxes screen of the dashboard
@index.route('/boxes')
def boxesDashboard():

    boxes_query = select(Box.id, Box.temperature_min, Box.temperature_max, Box.humidity_threshold, Box.weight_threshold, Box.acceleration_threshold, Box.position_latitude, Box.position_longitude)
    boxes_list = db.session.execute(boxes_query).all()

    boxes = []

    for box in boxes_list:
        id = box[0]
        temp_min = box[1] # list
        temp_max = box[2] # list
        humidity_max = box[3] # list
        weight_max = box[4] # list
        accel_max = box[5] # list
        lat = box[6]
        lon = box[7]

        temporal_serie_query = select(BoxTemporalSeries.timestamp, BoxTemporalSeries.temperature, BoxTemporalSeries.humidity, BoxTemporalSeries.weight, BoxTemporalSeries.acceleration)
        temporal_serie_list = db.session.execute(temporal_serie_query).all()

        temp_min = [temp_min for _ in temporal_serie_list]
        temp_max = [temp_max for _ in temporal_serie_list]
        humidity_max = [humidity_max for _ in temporal_serie_list]
        weight_max = [weight_max for _ in temporal_serie_list]
        accel_max = [accel_max for _ in temporal_serie_list]

        timestamps = []
        temperatures = []
        humidity = []
        weight = []
        acceleration = []

        for tuple in temporal_serie_list:
            timestamps.append(tuple[0])
            temperatures.append(tuple[1])
            humidity.append(tuple[2])
            weight.append(tuple[3])
            acceleration.append(tuple[4])

        boxes.append({
            "id": id,
            "timestamps": timestamps,
            "temperatures": temperatures,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "humidity": humidity,
            "humidity_max": humidity_max,
            "weight": weight,
            "weight_max": weight_max,
            "acceleration": acceleration,
            "accel_max": accel_max,
            "lat": lat,
            "lon": lon
        })

    return render_template('boxes.html', boxes = boxes)

# When requested returns the map screen of the dashboard
@index.route('/map')
def mapDashboard():
    boxes_query = select(Box)
    boxesTuple = db.session.execute(boxes_query).all()

    locationList = []

    for tuple in boxesTuple:
        box: Box = tuple[0]
        boxId = box.id
        position_query = select(Box.position_latitude,Box.position_longitude).where(Box.id == boxId)
        position = db.session.execute(position_query).first()
        locationList.append({
            'name': 'Box #' + str(boxId),
            'lat': position[0],
            'lng': position[1]
        })
    return render_template('map.html', locationList=locationList)

# Given a JSON POST request inserts into the database a new box
@index.route('/boxes/add_box', methods = ['POST'])
def createBox():
    json_request = request.get_json()
    
    id = json_request.get('id', -1)
    operator = json_request.get('operator', -1)
    temperature_min = json_request.get('temperature_min', 0)
    temperature_max = json_request.get('temperature_max', 280)
    humidity_threshold = json_request.get('humidity_threshold', 80)
    acceleration_threshold = json_request.get('acceleration_threshold', 80)
    weight_threshold = json_request.get('weight_threshold', 2000)
    tare = json_request.get('tare', 0)
    position_latitude = json_request.get('position_latitude', 41.9)
    position_longitude = json_request.get('position_longitude',12.4)
    
    box = Box(id, operator, temperature_min, temperature_max, humidity_threshold, acceleration_threshold, weight_threshold, tare, position_latitude, position_longitude)
    db.session.add(box)
    db.session.commit()

    return 'OK', '200 OK' 


# Given a JSON DELETE request removes a box from the database
@index.route('/boxes/remove_box', methods=['DELETE'])
def delBox():
    json_request = request.get_json()
    id = json_request.get('id', -1)
    if(id > 0):
        query = delete(Assignment).where(Assignment.id_box == id)
        db.session.execute(query)

        query = delete(Box).where( Box.id == id )
        db.session.execute(query)


        db.session.commit()
        return "OK","200 OK"

    return "INTERNAL ERROR", "500 ERROR"


# Given a JSON POST request modifies the Assignment table to associate the tool and the new box
@index.route('/boxes/<box_id>/add_tool', methods = ['POST'])
def addTool(box_id):
    json_request = request.get_json()
    tool_id = json_request.get('id', -1)

    tools_query = select(Assignment).where(Assignment.id_tool == tool_id)

    if db.session.execute(tools_query).one_or_none() != None:
        query = delete(Assignment).where(Assignment.id_tool == tool_id)
        db.session.execute(query)

    assignment = Assignment(tool_id, box_id)
    db.session.add(assignment)
    db.session.commit()

    return 'OK', '200 OK' 

# Given a JSON POST request modifies the Assignment table to disassociate the tool
@index.route('/boxes/<box_id>/remove_tool', methods = ['DELETE'])
def removeTool(box_id):
    json_request = request.get_json()
    id = json_request.get('id', -1)
    if(id > 0):
        query = delete(Assignment).where(Assignment.id_tool == id)
        db.session.execute(query)

        """ query = delete(Tool).where(Tool.id == id )
        db.session.execute(query) """
        db.session.commit()
        return "OK","200 OK"
    
    return "INTERNAL ERROR", "500 ERROR"

# Returns a list of all tool in a specific box
@index.route('/boxes/<box_id>/tool_list', methods = ['GET'])
def getTools(box_id):
    tools_query = select(Tool).join_from(Assignment, Tool).where(Assignment.id_box == box_id)
    tools = db.session.execute(tools_query).all()
    return jsonify_results(tools)

# Given a GET request returns the id of the operator associated to a box
# Given a JSON PUT request updates the id of the operator associated to a box 
@index.route('/boxes/<box_id>/id_operator', methods = ['GET', 'PUT'])
def idOperator(box_id):
    if request.method == 'PUT':
        json_request = request.get_json()
        id = json_request.get('id', -1)
        query = update(Box).where(Box.id == box_id).values(operator_id = id)

        db.session.execute(query)
        db.session.commit()

        return "OK","200 OK"
    else:
        query = select(Box.operator_id).where(Box.id == box_id)

        result = db.session.execute(query).first()

        return jsonify({'operator_id': result[0]})
    
# Given a GET request returns the thresholds of a specified box
# Given a JSON PUT request updates the thresholds values of a specified box
@index.route('/boxes/<box_id>/thresholds', methods = ['GET', 'PUT'])
def boxThresholds(box_id):
    if request.method == 'PUT':
        json_request = request.get_json()
        temperature_max = json_request.get('temperature_max', -1)
        temperature_min = json_request.get('temperature_min', -1)
        humidity_threshold = json_request.get('humidity_threshold', -1)
        acceleration_threshold = json_request.get('acceleration_threshold', -1)
        weight_threshold = json_request.get('weight_threshold', -1)
        tare = json_request.get('tare', -1)
        query = update(Box).where(Box.id == box_id).values(
            temperature_max = temperature_max,
            temperature_min = temperature_min,
            humidity_threshold = humidity_threshold,
            acceleration_threshold = acceleration_threshold,
            weight_threshold = weight_threshold,
            tare = tare
        )

        db.session.execute(query)
        db.session.commit()

        return "OK","200 OK"
    else:
        query = select(
            Box.temperature_min, 
            Box.temperature_max, 
            Box.humidity_threshold, 
            Box.acceleration_threshold, 
            Box.weight_threshold,
            Box.tare).where(Box.id == box_id)

        result = db.session.execute(query).first()

        return jsonify({
            "temperature_min": result[0],
            "temperature_max": result[1],
            "humidity_threshold": result[2],
            "acceleration_threshold": result[3],
            "weight_threshold": result[4],
            "tare": result[5]
            })



# Given a GET request returns the position of a specified box
# Given a JSON PUT request updates the position values of a specified box
@index.route('/boxes/<box_id>/position', methods=['GET','PUT'])
def getPos(box_id):
    if request.method == "GET":
        position_query = select(Box.position_latitude,Box.position_longitude).where(Box.id == box_id)
        position = db.session.execute(position_query).first()
        return jsonify({
            'latitude': position[0],
            'longitude': position[1]
        })
    else:
        json_request = request.get_json()
        longi=json_request.get('longitude', -1)
        lati=json_request.get('latitude', -1)
        query = update(Box).where(Box.id == box_id).values(position_latitude = lati , position_longitude = longi)
        db.session.execute(query)
        db.session.commit()
        return "OK","200 OK"
    
# Given a GET request returns the temporal_series of a specified box
# Given a JSON POST request adds the temporal series values of a specified box
@index.route('/boxes/<box_id>/temporal_serie', methods = ['POST', 'GET'])
def boxTemporalSerie(box_id):
    if request.method == 'POST':
        json_request = request.get_json()
        id = box_id
        error = json_request.get('error', False)
        temperature = json_request.get('temperature', -1)
        humidity = json_request.get('humidity', -1)
        acceleration = json_request.get('acceleration', -1)
        weight= json_request.get('weight', -1)

        temporalSerieItem = BoxTemporalSeries(id, error, temperature, humidity, acceleration, weight)
        db.session.add(temporalSerieItem)
        db.session.commit()

        query = select(BoxTemporalSeries).where(BoxTemporalSeries.id == box_id)
        results = db.session.execute(query).all()
        serieList = []

        for serieTuple in results:
            serieList.append(serieTuple[0])

        if len(serieList) >= TEMPORAL_SERIE_WINDOW:
            window: list[BoxTemporalSeries] = serieList[-TEMPORAL_SERIE_WINDOW:]
            average_temperature = 0
            average_humidity = 0
            average_acceleration = 0
            average_weight = 0
            for serie in window:
                average_temperature += serie.temperature / TEMPORAL_SERIE_WINDOW
                average_humidity += serie.humidity / TEMPORAL_SERIE_WINDOW
                average_acceleration += serie.acceleration / TEMPORAL_SERIE_WINDOW
                average_weight += serie.weight / TEMPORAL_SERIE_WINDOW

            new_temperature_max_threshold = average_temperature + TEMPERATURE_RANGE
            new_temperature_min_threshold = max(average_temperature - TEMPERATURE_RANGE, 0)
            new_humidity_threshold = average_humidity + HUMIDITY_ALLOWANCE
            new_acceleration_threshold = average_acceleration + ACCELERATION_ALLOWANCE
            new_weight_threshold = average_weight + WEIGHT_ALLOWANCE

            query = update(Box).where(Box.id == box_id).values(
                temperature_min = new_temperature_min_threshold,
                temperature_max = new_temperature_max_threshold,
                humidity_threshold = new_humidity_threshold,
                acceleration_threshold = new_acceleration_threshold,
                weight_threshold = new_weight_threshold,
            )

            db.session.execute(query)
            db.session.commit()

        return "OK","200 OK"
    else:
        query = select(BoxTemporalSeries).where(BoxTemporalSeries.id == box_id)
        results = db.session.execute(query).all()
        return jsonify_results(results)


@index.route('/tea', methods = ['GET'])
def tea():
    return "418 I'm a teapot"

# Returns the list of Boxes
@index.route('/boxes/list', methods = ['GET'])
def listBoxes():
    boxes_query = select(Box)
    boxes = db.session.execute(boxes_query).all()
    return jsonify_results(boxes)

    

# Adds a new tool in the Tool table
@index.route('/tools/add_tool', methods = ['POST'])
def createTool():
    json_request = request.get_json()
    id = json_request.get('id', -1)
    uuid = json_request.get('uuid', ' ')
    name = json_request.get('name', 'beautiful_tool')
    box_id = json_request.get('box_id', None)

    tool = Tool(id, uuid, name)
    db.session.add(tool)
    db.session.commit()

    assignment = Assignment(id, box_id)
    db.session.add(assignment)
    db.session.commit()

    return 'OK', '200 OK'


# removes a specific tool
@index.route('/tools/remove_tool', methods=['DELETE'])
def delTool():
    json_request = request.get_json()
    id = json_request.get('id', -1)
    if(id > 0):
        query = delete(Assignment).where(Assignment.id_tool == id)
        db.session.execute(query)

        query = delete(Tool).where(Tool.id == id )
        db.session.execute(query)
        db.session.commit()
        return "OK","200 OK"
    
    return "INTERNAL ERROR", "500 ERROR"

# Updates a specific tool
@index.route('/tools/<id_tool>/update_tool', methods = ['PUT'])
def updateTool(id_tool):
    json_request = request.get_json()
    id_new = json_request.get('id', -1)
    uuid_new = json_request.get('uuid', -1)
    name_new = json_request.get('name', -1)
    box_id = json_request.get('box_id', -1)

    if id_new != -1:
        query = update(Tool).where(Tool.id == id_tool).values(id=id_new)
        db.session.execute(query)
        db.session.commit()
    if uuid_new != -1:
        query = update(Tool).where(Tool.id == id_tool).values(uuid=uuid_new)
        db.session.execute(query)
        db.session.commit()
    if name_new != -1:
        query = update(Tool).where(Tool.id == id_tool).values(name=name_new)
        db.session.execute(query)
        db.session.commit()
    
    return 'OK', '200 OK'

# Returns a tool given his id
@index.route('/tools/<id_tool>', methods = ['GET'])
def tool(id_tool):
    query = select(Tool).where(Tool.id == id_tool)

    result = db.session.execute(query).first()

    return jsonify({'id': result[0].id, 'UUID': result[0].uuid, 'name': result[0].name})

# Returns a tool given his uuid
@index.route('/tools/by_uuid/<uuid>', methods = ['GET'])
def toolByUUID(uuid):
    query = select(Tool).where(Tool.uuid == uuid)

    result = db.session.execute(query).first()

    return jsonify({'id': result[0].id, 'UUID': result[0].uuid, 'name': result[0].name})


# Given a GET request returns he box where the specific tool is in
# Given a JSON PUT request updates the box where the specific tool is in
@index.route('/tools/<id_tool>/box', methods = ['GET', 'PUT'])
def toolBox(id_tool):
    if request.method=='GET':
        query = select(Assignment.id_box).where(Assignment.id_tool == id_tool)

        result = db.session.execute(query).first()

        return jsonify({'id_box': result[0]})
    else:
        json_request = request.get_json()

        box = json_request.get('id_box', -1)
        
        query = update(Assignment).where(Assignment.id_tool == id_tool).values(id_box=box)
        
        db.session.execute(query)
        db.session.commit()
        return 'OK', '200 OK' 

# Returns all the tools
@index.route('/tools/list', methods = ['GET'])
def listTools():
    tools_query = select(Tool)
    tools = db.session.execute(tools_query).all()
    return jsonify_results(tools)
    


# Returns all operators
@index.route('/operators/list', methods = ['GET'])
def listOperatorS():
    operators_query = select(Operator)
    operators = db.session.execute(operators_query).all()
    return jsonify_results(operators)

# Given a JSON POST request adds the operator to the database
@index.route('/operators/add_operator', methods = ['POST'])
def createOperator():
    json_request = request.get_json()
    id = json_request.get('id', -1)
    name = json_request.get('name', 'smooth_operator')
    
    operator = Operator(id, name)

    db.session.add(operator)
    db.session.commit()

    return 'OK', '200 OK'


# Given a JSON DELETE request removes the operator from the database
@index.route('/operators/remove_operator', methods=['DELETE'])
def delOperator():
    json_request = request.get_json()
    id_op = json_request.get('id', -1)
    
    if id_op != -1:
        query = delete(Operator).where(Operator.id == id_op)
        db.session.execute(query)
        db.session.commit()
        return "OK","200 OK"
    
    return "INTERNAL ERROR - ID ERROR", "500 ERROR" 