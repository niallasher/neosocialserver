import click
from socialserver import application


@click.group()
def cli():
    pass


@click.command()
@click.option('port', '--port', '-p', default=12345, help='Port to host on. Default is 12345.')
@click.option('bind_addr', '--bind-addr', '-b', default='0.0.0.0', help='Address to bind to. Default is 0.0.0.0.')
def devel_run(port, bind_addr):
    application.run(host=bind_addr, port=port, debug=True)


@click.command()
def test():
    click.echo("This is just a test")


# register commands with cli group
cli.add_command(devel_run)
cli.add_command(test)
