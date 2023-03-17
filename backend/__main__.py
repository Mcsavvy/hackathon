import rich
import uvicorn
import click
from qdrant_client import QdrantClient
from rich import box
from rich.panel import Panel

from . import config
from .api import salesman
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


def build():
    if config.LAPTOP_VECTORS.exists():
        console.log(f"Embeddings found in {config.LAPTOP_VECTORS}.")
    else:
        with console.status("Embedding Laptops"):
            embed_laptops()

    try:
        qdrant.get_collection(config.LAPTOPS_COLLECTION_NAME)
        console.log(f"Collection {config.LAPTOPS_COLLECTION_NAME!r} exists.")
        # qdrant.delete_collection(config.LAPTOPS_COLLECTION_NAME)
    except Exception as exc:
        with console.status("Uploading Embeddings"):
            upload_to_cluster()


def print_results(results: list):
    """Print the results of a search."""
    for result in results:
        panel = Panel(
            result["description"],
            border_style="yellow",
            title=result["name"],
            subtitle=result["mpn"],
            subtitle_align="center",
            box=box.SQUARE,
        )
        rich.print(panel)
    console.rule()


def interactive():
    """Run SalesMan  Interactively."""
    while True:
        try:
            text = console.input("search for a laptop: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        results = searcher.search(text)
        print_results(results)


def web():
    """Serve Salesmam On The Web."""
    uvicorn.run(salesman, host="localhost", port=8000)


web()
