from argparse import ArgumentParser
from socialserver.util.config import config
from socialserver import application
import click


def run_debug():
    if config.debug.auto_reload_templates:
        print("Debug: templates auto reloading")
        application.config['TEMPLATES_AUTO_RELOAD'] = True
    if config.debug.zero_max_file_age:
        print("Debug: max file age is zero")
        application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    application.run(host=config.network.host, port=config.network.port,
                    debug=True)


# parser = ArgumentParser()
# parser.add_argument("-d", "--debug", help="Run in debug mode",
#                     action="store_true")
# args = parser.parse_args()
# print("socialserver3 dev build")
# if args.debug:
#     run_debug()
# else:
#     print("Run with -d/--debug flag to run in debug mode")

@click.group()
def cli():
    pass


@click.command()
@click.option('port', '--port', default=12345, help='Port to host on. Default is 12345.')
@click.option('bind_addr', '--bind-addr', default='0.0.0.0', help='Address to bind to. Default is 0.0.0.0.')
def devel_run(port, bind_addr):
    application.run(host=bind_addr, port=port, debug=True)


@click.command()
def test():
    click.echo("This is just a test")


cli.add_command(devel_run)
cli.add_command(test)

if __name__ == "__main__":
    cli()
