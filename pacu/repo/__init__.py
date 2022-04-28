import typer

# Reference sub-commands explicitly, so they don't need to have specific __init__.py files in them.
from . import list

app = typer.Typer()

# Sub-Commands
app.command(name="list")(list.main)

# This file can be run directly for testing if it's helpful.
if __name__ == "__main__":
    app()