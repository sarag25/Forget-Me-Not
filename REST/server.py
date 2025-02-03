# server
# db.session

from flask import Flask
from config import Config
from database import db
from index import index
from mqtt_listener import mqtt

appname = "REST_server"
app = Flask(appname)

app.register_blueprint(index)
myconfig = Config
app.config.from_object(myconfig)


@app.errorhandler(404)
def page_not_found(error):
    return 'Error', 404


if __name__ == '__main__':
    db.init_app(app)
    mqtt.init_app(app)
    if True:  # first time (?)
        with app.app_context():
            db.create_all()

    app.run(host=app.config.get('FLASK_RUN_HOST','localhost'),
            port=app.config.get('FLASK_RUN_PORT',8080))
