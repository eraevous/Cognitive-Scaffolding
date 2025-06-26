import typer

import cli.batch_ops as batch_ops
import cli.classify as classify
import cli.cluster as cluster
import cli.embed as embed
import cli.pipeline as pipeline
import cli.tokens as tokens

app = typer.Typer()

app.add_typer(classify.app, name="classify")
app.add_typer(batch_ops.app, name="batch")
app.add_typer(embed.app, name="embed")
app.add_typer(cluster.app, name="cluster")
app.add_typer(pipeline.app, name="pipeline")
app.add_typer(tokens.app, name="tokens")

if __name__ == "__main__":
    app()
