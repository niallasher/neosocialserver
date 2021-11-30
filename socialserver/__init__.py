from flask import Flask
from flask.templating import render_template
from socialserver.util.config import config

application = Flask(__name__)


@application.get('/')
def landing_page():
    return render_template('server_landing.html')


def app():
    pass


"""
    run_debug
    Run using local flask debugging server.
    Used when invoking main.py with the -d/--debug flag.
    NEVER USE THIS IN PRODUCTION!
"""
