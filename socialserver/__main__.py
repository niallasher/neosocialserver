from socialserver.util.config import config
from socialserver import application
import socialserver.util.image


def run_debug():
    if config.debug.auto_reload_templates:
        print("Debug: templates auto reloading")
        application.config['TEMPLATES_AUTO_RELOAD'] = True
    if config.debug.zero_max_file_age:
        print("Debug: max file age is zero")
        application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    application.run(host=config.network.host, port=config.network.port,
                    debug=True)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", help="Run in debug mode",
                        action="store_true")
    args = parser.parse_args()
    print("socialserver3 dev build")
    if args.debug:
        run_debug()
    else:
        print("Run with -d/--debug flag to run in debug mode")
