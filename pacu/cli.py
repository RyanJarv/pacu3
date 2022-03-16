import typer
import pacu.aws

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

# Additional instances of typer can be added as subcommands.
app.add_typer(name="aws", typer_instance=pacu.aws.app)

if __name__ == '__main__':
    app(prog_name="pacu")
