import rich
import click
from qdrant_client import QdrantClient
from rich import box
from rich.panel import Panel

from . import config
from .api import app
from .laptops.embed_laptops import (
    NeuralSearcher,
    cohere,
    embed_laptops,
    qdrant,
    upload_to_cluster,
)
from .schema import walk_json_tree

searcher = NeuralSearcher(config.LAPTOPS_COLLECTION_NAME)
console = rich.get_console()

@click.group()
def cli():
    """Operate Salesman from command line."""
    pass


@cli.command()
@click.option("-e", "--embed", is_flag=True)
@click.option("-u", "--upload", is_flag=True)
def build(embed, upload):
    """Embed and Upload Data."""
    if config.LAPTOP_VECTORS.exists() and not embed:
        console.log(f"Embeddings found in {config.LAPTOP_VECTORS}.")
    else:
        with console.status("Embedding Laptops"):
            embed_laptops()
    try:
        qdrant.get_collection(config.LAPTOPS_COLLECTION_NAME)
        if not upload:
            console.log(
                f"Collection {config.LAPTOPS_COLLECTION_NAME!r} exists.")
    except Exception as exc:
        upload = True
    if upload:
        with console.status("Uploading Embeddings"):
            upload_to_cluster()


def print_results(results: list):
    """Print the results of a search."""
    for result in results:
        body = [
            f"[blue]prices: [/] " + " ".join(
                f"[on red]{p['price']:.2f}[/]" for p in result['prices']
            ),
            f"[blue]info: [/] {result['info']}",
            f"[blue]target users: [/] {result['target_user']}",
            result['description']
        ]
        panel = Panel(
            "\n\n".join(body),
            border_style="yellow",
            title=result["name"],
            subtitle=result["mpn"],
            subtitle_align="center",
            box=box.SQUARE,
        )
        rich.print(panel)
    console.rule()

@cli.command()
def interactive():
    """Run SalesMan interactively."""
    while True:
        try:
            text = console.input("search for a laptop: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        results = searcher.search(text)
        print_results(results)

@cli.command()
def web():
    """Serve Salesman on the web."""
    app.run()


cli()
