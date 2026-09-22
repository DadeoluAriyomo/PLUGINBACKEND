from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO





from config import Config


db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(
    cors_allowed_origins="*"
)


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    CORS(app)

    from app.models import User
    from app.routes.auth import auth
    from app.routes.categories import categories
    from app.routes.jobs import jobs
    from app.routes.vendors import vendors
    from app.routes.bids import bids
    from app.routes.chat import chat

    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(categories, url_prefix="/api")
    app.register_blueprint(jobs, url_prefix="/api")
    app.register_blueprint(vendors, url_prefix="/api")
    app.register_blueprint(bids, url_prefix="/api")
    app.register_blueprint(chat, url_prefix="/api")
    

    with app.app_context():
        db.create_all()

    return app

# IMPORTANT:
# Keep this outside create_app()
import app.socket_events