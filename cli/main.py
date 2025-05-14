import typer
import classification
import batch_ops
import clustering

app = typer.Typer()

app.add_typer(classification.app, name="classify")
app.add_typer(batch_ops.app, name="batch")
app.add_typer(clustering.app, name="cluster")

if __name__ == "__main__":
    app()
