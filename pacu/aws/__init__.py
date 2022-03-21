import typer

# Reference sub-commands explicitly, so they don't need to have specific __init__.py files in them.
from pacu.aws import creds

from . import user
from . import utils
from . import role

app = typer.Typer(help='Modules relating to AWS', short_help='Modules relating to AWS.')

#Sub-commands of `pacu aws` get added here.
app.add_typer(user.app, name='users')
app.add_typer(role.app, name='role')
app.add_typer(creds.app, name='creds')

# I'm sure there's a better way to do this, but this works for now.
# We just want these to show up directly under the `pacu aws` subcommand.
app.command(help='Prints out the current AWS user.', short_help='whoami cmd')(utils.whoami)
app.command()(utils.login)

# This file can be run directly for testing if it's helpful.
if __name__ == "__main__":
    app()