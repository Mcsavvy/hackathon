"""
NEURAL SEARCH.

This project is a sample project gotten from
https://qdrant.tech/articles/neural-search-tutorial/#

It utilizes the power of Cohere to create embeddings and
then Qdrant to do quick vector searches.
"""

import json
import os
import sys
from typing import TypedDict
import time

import cohere
import numpy as np
import pandas as pd
import rich
from cohere.embeddings import Embeddings
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams
from rich.panel import Panel
from rich.progress import Progress
from rich import get_console
from tqdm import tqdm
from rich import box

PAYLOAD_FILE = "startups.json"
VECTORS_FILE = "startups.npy"
BATCH_SIZE = 256
COLLECTION_NAME = "startups"

co = cohere.Client(os.environ["COHERE_API_KEY"])
qd = QdrantClient(
    host=os.environ["QDRANT_HOST"],
    port=int(os.environ["QDRANT_PORT"])
)
console = get_console()


class StartUp(TypedDict):
    """A startup entry in the database."""

    name: str
    images: str
    alt: str
    description: str
    link: str
    city: str


def get_embeddings(texts: list[str]) -> np.ndarray:
    """
    Create embeddings from a list of strings.

    The length of returned list of embeddings corresponds with the length
    of the input list.

    Args:
        texts: a list of strings to be used to create embeddings
    Returns:
        a list of embeddings
    """
    for index, text in enumerate(texts):
        if len(text) > 511:
            # TODO: summarize text
            pass
        elif not text:
            raise Exception(f"texts[{index}] is empty")
    embeddings: list[list[float]] = []
    embedding: list[float]
    batch_size = 96
    batch_count = 1
    batch: list[str] = []
    for text in texts:
        batch.append(text)
        if len(batch) >= batch_size:
            with console.status(f"Embedding batch {batch_count}...") as status:
                start = time.perf_counter()
                response = co.embed(text=batch, model='multilingual-22-12')
                duration = divmod(time.perf_counter() - start, 60)
                console.log(
                    "Done embedding in {} minute(s) and {:.4f} seconds ✔"
                    .format(*duration))
            embeddings.append(response.embeddings)
            batch_count += 1
            batch = []
    if len(batch) > 0:
        with console.status(f"Embedding batch {batch_count}...") as status:
            start = time.perf_counter()
            response = co.embed(text=batch, model='multilingual-22-12')
            duration = divmod(time.perf_counter() - start, 60)
            console.log("Done embedding in {} minute(s) and {:.4f} seconds ✔"
                        .format(*duration))
        embeddings.append(response.embeddings)
        batch_count += 1
        batch = []
    vectors = np.concatenate(embeddings)
    return vectors


def embed_payload() -> None:
    """
    Create vector embeddings.

    The embeddings created are then converted to
    ndarrays and persisted to a file.
    """
    # load data
    df = pd.read_json(PAYLOAD_FILE, lines=True)
    texts: list[str] = []
    for row in tqdm(df.itertuples()):
        description = f"{row.alt}. {row.description}. {row.city}"
        texts.append(description)
    embeddings: np.ndarray = get_embeddings(texts)
    np.save(VECTORS_FILE, embeddings)


def create_collection(collection_name: str):
    """
    Upload the embeddings to your qdrant instance.

    Arg:
        collection_name: name of collection
    """
    with open(PAYLOAD_FILE) as fd:
        # payload is now a list of startup data
        payload = list(map(json.loads, fd))

    # Here we load all vectors into memory,
    # numpy array works as iterable for itself.
    # Other option would be to use Mmap, if we don't want to load all data
    # into RAM
    vectors = np.load(VECTORS_FILE)
    vector_size = len(vectors[0])
    # The recreate_collection function first tries to remove an existing
    # collection with the same name.
    # This is useful if you are experimenting and running the script
    # several times.
    qd.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    qd.upload_collection(
        collection_name=collection_name,
        vectors=vectors,
        payload=payload,
        ids=None,  # Vector ids will be assigned automatically
        batch_size=BATCH_SIZE,  # How many vectors will be uploaded at once?
        parallel=10
    )


class NeuralSearcher:
    """A neural searcher."""

    def __init__(self, collection_name):
        """
        Initialize a neural searcher.

        Args:
            collection_name: the name of the collection to use when searching
        """
        self.collection_name = collection_name
        # Initialize encoder model
        self.model = co
        # initialize Qdrant client
        self.qdrant_client = qd

    def search(self, text: str):
        """
        Query the database.

        Args:
            text: text to use to query database
        """
        # Convert text query into vector
        vector = self.model.embed([text]).embeddings[0]
        # print(f"Vectors: {vector}")

        # Use `vector` for search for closest vectors in the collection
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=np.array(vector),
            query_filter=None,  # We don't want any filters for now
            limit=5  # 5 the most closest results is enough
        )
        # `search_result` contains found vector ids with similarity
        # scores along with the stored payload
        # In this function we are interested in payload only
        payloads = [hit.payload for hit in search_result]
        return payloads


def print_results(results: list[StartUp]):
    """Print the results of a search."""
    for result in results:
        panel = Panel(
            result["description"],
            border_style="yellow",
            title=f"{result['name']} ({result['city']})",
            subtitle=result["link"],
            subtitle_align="right",
            box=box.SQUARE)
        rich.print(panel)
        print()
    console.rule()


if __name__ == "__main__":
    if not os.path.isfile(PAYLOAD_FILE):
        print(f"Payload file {PAYLOAD_FILE} doesn't exist!", file=sys.stderr)
        exit(1)

    if os.path.isfile(VECTORS_FILE):
        # print(f"Embeddings already exists.")
        pass
    else:
        print(f"Creating embeddings...")
        embed_payload()
    try:
        qd.get_collection(COLLECTION_NAME)
        # print(f"Collection {COLLECTION_NAME!r} already exists.")
    except UnexpectedResponse as exc:
        if exc.status_code == 404:
            with console.status(
                    f"Creating collection {COLLECTION_NAME!r}"):
                create_collection("startups")
        else:
            raise
    searcher = NeuralSearcher(COLLECTION_NAME)
    while True:
        try:
            text = console.input("search for a startup: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        results = searcher.search(text)
        print_results(results)
    # print(type(result))
    # print(result)
