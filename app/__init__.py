from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from app import routes
    app.register_blueprint(routes.main)

    return app