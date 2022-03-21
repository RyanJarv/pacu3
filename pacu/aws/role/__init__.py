import typer

# Reference sub-commands explicitly, so they don't need to have specific __init__.py files in them.
from . import create, delete
from . import trust

app = typer.Typer()

# Sub-Commands
app.command(name="create")(create.app)
app.command(name="delete")(delete.app)

# Sub-Modules
app.add_typer(trust.app, name='trust')

# This file can be run directly for testing if it's helpful.
if __name__ == "__main__":
    app()