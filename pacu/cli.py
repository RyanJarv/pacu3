import typer
from pacu import aws
from pacu import repo

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

# Additional instances of typer can be added as subcommands.
app.add_typer(name="aws", typer_instance=aws.app)
app.add_typer(name="repo", typer_instance=repo.app)

if __name__ == '__main__':
    app(prog_name="pacu")
