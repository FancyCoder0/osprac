from flask import Flask
from flask import request, url_for
# from flask_bootstrap import Bootstrap

from config import config

def create_app(config_name):
    """ factory function for create app
    :param config_name
    :return: app object
    """
    app = Flask(__name__)

    # set up config
    app.config.from_object(config[config_name])

    # setup github-flask
    # bootstrap.init_app(app)
    
    from .main import main as main_blueprint  # main blue print
    app.register_blueprint(main_blueprint)

    return app

from app.main import views
