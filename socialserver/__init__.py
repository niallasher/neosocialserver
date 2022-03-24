#  Copyright (c) Niall Asher 2022

from socialserver.util.output import console
from socialserver.app import create_app
from socialserver.util.post import start_unprocessed_post_thread

application = create_app()
