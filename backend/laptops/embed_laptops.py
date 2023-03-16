from ..config import (
    LAPTOP_VECTORS,
    LAPTOP_PAYLOADS,
    LAPTOP_DB,
    LAPTOPS_COLLECTION_NAME,
    QDRANT_BATCH_SIZE,
    QDRANT_INIT_KWARGS,
    COHERE_API_KEY,
)
import json
import os
import sys
import time

from cohere import Client as CohereClient
import numpy as np
import pandas as pd
import rich
# from cohere.embeddings import Embeddings
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams
from rich.panel import Panel
from rich.progress import Progress
from rich import get_console
from tqdm import tqdm
from rich import box
# from IPython.terminal.embed import embed
from collections import defaultdict


cohere = CohereClient(COHERE_API_KEY)
qdrant = QdrantClient(**QDRANT_INIT_KWARGS)
console = get_console()


def embed_laptops() -> None:
    """Embed all laptop classifications."""
    payloads = dict[int, list[str]]()
    embeddings: list[list[float]] = []

    for path in LAPTOP_PAYLOADS:
        classifications = json.loads(path.read_text())
        for index, classification in enumerate(classifications):
            # each item belongs to an item
            if isinstance(classification, list):
                payload = " ".join(c.strip() for c in classification)
            else:
                payload = str(classification).strip()
            payloads.setdefault(index, list()).append(payload)

    batch_counter = 1
    payload_size = len(payloads)
    no_of_batches, r = divmod(payload_size, 96)
    if r != 0:
        no_of_batches += 1
    batch: list = []
    for payload_set in payloads.values():
        batch.append(" - ".join(payload_set))
        if len(batch) >= 96:
            console.log(
                f"Embedding batch {batch_counter} of {no_of_batches}...")
            resp = cohere.embed(batch, model='multilingual-22-12')
            embeddings.append(resp.embeddings)
            batch_counter += 1
            batch = []
    if len(batch) > 0:
        console.log(
            f"Embedding batch {batch_counter} of {no_of_batches}...")
        resp = cohere.embed(batch, model='multilingual-22-12')
        embeddings.append(resp.embeddings)
        batch_counter += 1
        batch = []
    vectors = np.concatenate(embeddings)
    console.log("saving embeddings...")
    np.save(LAPTOP_VECTORS, vectors)
    console.log("done embedding ✔")


def upload_to_cluster():
    """Upload embeddings to a qdrants cluster."""
    # load laptops data
    console.log("Loading data...")
    data = json.loads(LAPTOP_DB.read_text())
    # load embeddings
    console.log("Loading embeddings...")
    vectors = np.load(LAPTOP_VECTORS)
    # get length of embeddings
    vector_size = len(vectors[0])

    # create collection.
    # NOTE: would be recreated if it exists.
    console.log(
        f"Creating collection {LAPTOPS_COLLECTION_NAME!r}...")
    qdrant.recreate_collection(
        collection_name=LAPTOPS_COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )

    # upload collection
    console.log(
        f"Uploading collection {LAPTOPS_COLLECTION_NAME!r}...")
    qdrant.upload_collection(
        collection_name=LAPTOPS_COLLECTION_NAME,
        vectors=vectors,
        payload=data,
        ids=None,
        batch_size=QDRANT_BATCH_SIZE,
        parallel=10    
    )
    console.log("Done ✔")

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
        self.model = cohere
        # initialize Qdrant client
        self.qdrant_client = qdrant

    def search(self, text: str):
        """
        Query the database.

        Args:
            text: text to use to query database
        """
        # Convert text query into vector
        vector = self.model.embed([text], model='multilingual-22-12').embeddings[0]
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
