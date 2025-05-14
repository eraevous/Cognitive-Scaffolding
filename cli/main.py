import typer
import cli.classify as classify
import cli.batch_ops as batch_ops
import cli.embed as embed
#import clustering

app = typer.Typer()

app.add_typer(classify.app, name="classify")
app.add_typer(batch_ops.app, name="batch")
app.add_typer(embed.app, name="embed")
#app.add_typer(clustering.app, name="cluster")

if __name__ == "__main__":
    app()
