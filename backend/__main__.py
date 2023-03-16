from .schema import walk_json_tree
from .laptops.classify_laptop import (
    classify_based_on_specs
)
from .laptops.embed_laptops import (
    embed_laptops, upload_to_cluster,
    NeuralSearcher, cohere, qdrant
)
from . import config
import rich
from qdrant_client.http.exceptions import UnexpectedResponse
from .laptops.classify_laptop import generate_description

console = rich.get_console()
from qdrant_client import QdrantClient
from rich import box
from rich.panel import Panel


if config.LAPTOP_VECTORS.exists():
    console.log(
        f"Embeddings found in {config.LAPTOP_VECTORS}.")
else:
    with console.status("Embedding Laptops"):
        embed_laptops()

try:
    qdrant.get_collection(
        config.LAPTOPS_COLLECTION_NAME)
    console.log(
        f"Collection {config.LAPTOPS_COLLECTION_NAME!r} exists.")
except Exception as exc:
    with console.status("Uploading Embeddings"):
        upload_to_cluster()


searcher = NeuralSearcher(config.LAPTOPS_COLLECTION_NAME)


def print_results(results: list):
    """Print the results of a search."""
    for result in results:
        panel = Panel(
            generate_description(result),
            border_style="yellow",
            title=result["name"],
            subtitle=result["mpn"],
            subtitle_align="center",
            box=box.SQUARE)
        rich.print(panel)
    console.rule()


while False:
    try:
        text = console.input("search for a laptop: ")
    except (EOFError, KeyboardInterrupt):
        print()
        break
    results = searcher.search(text)
    print_results(results)

generate_description()