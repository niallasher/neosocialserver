from rich.console import Console
from rich.traceback import install as install_traceback_handler

# this allows rich to pretty print our
# tracebacks. takes care of having to
# describe errors, since it's incredibly
# readable. also looks cool.

# we do this here since it's the first socialserver
install_traceback_handler()

console = Console()
