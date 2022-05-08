import typer
import logging
from pacu import aws

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

# Additional instances of typer can be added as subcommands.
app.add_typer(name="aws", typer_instance=aws.app)

if __name__ == '__main__':
    app(prog_name="pacu")


@app.callback()
def setup_logging(debug: bool = False, verbose: bool = False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARN)