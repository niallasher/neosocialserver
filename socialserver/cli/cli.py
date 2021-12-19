import click
from socialserver import application
from socialserver.cli.mkuser import mk_user_interactive
from socialserver.cli.uploadimage import upload_image


@click.group()
def cli():
    pass


@click.command()
@click.option('port', '--port', '-p', default=12345, help='Port to host on. Default is 12345.')
@click.option('bind_addr', '--bind-addr', '-b', default='0.0.0.0', help='Address to bind to. Default is 0.0.0.0.')
@click.option('template_auto_reload', '--template-auto-reload', '-t', default=False,
              help='Enable template auto reloading. Default is False.')
@click.option('max_file_age', '--max-file-age', '-m', default=0, help='Max file age. Default is 0.')
def devel_run(port, bind_addr, template_auto_reload, max_file_age):
    if template_auto_reload:
        application.config['TEMPLATES_AUTO_RELOAD'] = True
    application.config['SEND_FILE_MAX_AGE_DEFAULT'] = max_file_age
    application.run(host=bind_addr, port=port, debug=True)


@click.command()
@click.option('interactive', '--interactive', '-i', default=True, help='Enable interactive mode.')
def mkuser(interactive):
    if not interactive:
        print("Sorry, non-interactive mode is not avaliable yet.")
    else:
        mk_user_interactive()


@click.command()
@click.argument('path')
def uploadimage(path):
    upload_image(path)


# register commands with cli group
cli.add_command(uploadimage)
cli.add_command(devel_run)
cli.add_command(mkuser)
