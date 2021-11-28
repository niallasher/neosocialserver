from flask import Flask
from flask.templating import render_template
from configutil import config

app = Flask(__name__)


@app.get('/')
def landing_page():
    return render_template('server_landing.html')


if __name__ == '__main__':
    if config.debug.auto_reload_templates:
        print("Debug: templates auto reloading")
        app.config['TEMPLATES_AUTO_RELOAD'] = True
    if config.debug.zero_max_file_age:
        print("Debug: max file age is zero")
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    app.run(host=config.network.host, port=config.network.port,
            debug=config.debug.enable_flask_debug_mode)
