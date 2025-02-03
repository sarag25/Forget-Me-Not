from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

# creation of database tables


class BoxTemporalSeries(db.Model,SerializerMixin):
    __tablename__= "boxtemporalseries"
    id = db.Column(db.Integer, primary_key = True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False,  default=datetime.utcnow, primary_key = True)
    error = db.Column(db.Boolean)
    temperature = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    acceleration = db.Column(db.Integer)
    weight = db.Column(db.Integer)

    def __init__(self, id, error, temperature, humidity, acceleration, weight):
        self.id = int(id)
        self.error = bool(error)
        self.temperature = int(temperature)
        self.humidity = int(humidity)
        self.acceleration = int(acceleration)
        self.weight = int(weight)
        

class Tool(db.Model,SerializerMixin):
    __tablename__= "tool"
    id = db.Column(db.Integer,primary_key = True)
    uuid = db.Column(db.String)
    name = db.Column(db.String)

    def __init__(self, id, uuid, name):
        self.name = str(name)
        self.uuid = str(uuid)
        self.id = int(id)

    def json(self):
        return jsonify(
            {
                'id': self.id,
                'uuid': self.uuid,
                'name': self.name
            }
        )


class Operator(db.Model,SerializerMixin):
    __tablename__ = "operator"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

    def __init__(self, id, name):
        self.name = str(name)
        self.id = int(id)


class Box(db.Model,SerializerMixin):
    __tablename__= "box"
    id = db.Column(db.Integer, primary_key = True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.id'))
    temperature_min = db.Column(db.Integer)
    temperature_max = db.Column(db.Integer)
    humidity_threshold = db.Column(db.Integer)
    acceleration_threshold = db.Column(db.Integer)
    weight_threshold = db.Column(db.Integer)
    tare = db.Column(db.Integer)
    position_latitude = db.Column(db.Float)
    position_longitude = db.Column(db.Float)

    def __init__(self, id, operator_id, temperature_min, temperature_max, humidity_threshold, acceleration_threshold, weight_threshold, tare, position_latitude, position_longitude):
        self.id = int(id)
        self.operator_id = int(operator_id)
        self.temperature_min = int(temperature_min)
        self.temperature_max = int(temperature_max)
        self.humidity_threshold = int(humidity_threshold)
        self.acceleration_threshold = int(acceleration_threshold)
        self.weight_threshold = int(weight_threshold)
        self.tare = int(tare)
        self.position_latitude = float(position_latitude)
        self.position_longitude = float(position_longitude)


class Assignment(db.Model,SerializerMixin):
    __tablename__= "assignment"
    id_tool = db.Column(db.Integer,db.ForeignKey('tool.id'),primary_key = True)
    id_box = db.Column(db.Integer,db.ForeignKey('box.id') )

    def __init__(self, id_tool,id_box):
        self.id_tool = int(id_tool)
        self.id_box = id_box