import typer
#import clustering
#import classification
import batch_ops

app = typer.Typer()

# Attach sub-apps
#app.add_typer(clustering.app, name="cluster")
#app.add_typer(classification.app, name="classify")
app.add_typer(batch_ops.app, name="batch")
# app.add_typer(utility.app, name="utils")  # if you want

if __name__ == "__main__":
    app()