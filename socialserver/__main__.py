from argparse import ArgumentParser
from socialserver.util.config import config
from socialserver import application
from socialserver.cli import cli


def run_debug():
    if config.debug.auto_reload_templates:
        print("Debug: templates auto reloading")
        application.config['TEMPLATES_AUTO_RELOAD'] = True
    if config.debug.zero_max_file_age:
        print("Debug: max file age is zero")
        application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


if __name__ == "__main__":
    # use the cli if calling the module directly,
    # to allow for convenient launch and admin etc
    cli()
