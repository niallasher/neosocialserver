#  Copyright (c) Niall Asher 2022

import click
from socialserver.cli.admin.getstats import print_server_statistics
from socialserver.cli.admin.create_user import create_user_account
from socialserver.cli.admin.usermod import verify_user, unverify_user, mod_user, unmod_user, make_user_admin, \
    remove_user_admin_role


@click.group()
def cli():
    pass


@click.group()
def admin():
    pass


@click.command()
def get_stats():
    print_server_statistics()


@click.group()
def user():
    pass


@click.command()
def create():
    create_user_account()
    pass


@click.command()
@click.argument("username")
def verify(username):
    verify_user(username)


@click.command()
@click.argument("username")
def unverify(username):
    unverify_user(username)


@click.command()
@click.argument("username")
def make_mod(username):
    mod_user(username)


@click.command()
@click.argument("username")
def revoke_mod(username):
    unmod_user(username)


@click.command()
@click.argument("username")
def make_admin(username):
    make_user_admin(username)


@click.command()
@click.argument("username")
def revoke_admin(username):
    remove_user_admin_role(username)


user.add_command(verify)
user.add_command(unverify)
user.add_command(make_mod)
user.add_command(revoke_mod)
user.add_command(make_admin)
user.add_command(revoke_admin)
user.add_command(create)

admin.add_command(user)
admin.add_command(get_stats)


@click.command()
@click.option(
    "port", "--port", "-p", default=12345, help="Port to host on. Default is 12345."
)
@click.option(
    "bind_addr",
    "--bind-addr",
    "-b",
    default="0.0.0.0",
    help="Address to bind to. Default is 0.0.0.0.",
)
@click.option(
    "template_auto_reload",
    "--template-auto-reload",
    "-t",
    default=False,
    help="Enable template auto reloading. Default is False.",
)
@click.option(
    "max_file_age",
    "--max-file-age",
    "-m",
    default=0,
    help="Max file age. Default is 0.",
)
def devel_run(port, bind_addr, template_auto_reload, max_file_age):
    from socialserver import application
    if template_auto_reload:
        application.config["TEMPLATES_AUTO_RELOAD"] = True
    application.config["SEND_FILE_MAX_AGE_DEFAULT"] = max_file_age
    application.run(host=bind_addr, port=port, debug=True)


cli.add_command(devel_run)
cli.add_command(admin)
