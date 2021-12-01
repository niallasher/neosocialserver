from argparse import ArgumentParser
from socialserver.util.config import config
from socialserver import application
from socialserver.cli.cli import cli

if __name__ == "__main__":
    # use the cli if calling the module directly,
    # to allow for convenient launch and admin etc
    cli()
