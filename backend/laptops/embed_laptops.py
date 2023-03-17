import json
import os
import sys
import time

import numpy as np
import rich
from cohere import Client as CohereClient
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams
from rich import box, get_console
from rich.panel import Panel
from rich.progress import Progress

from ..config import (
    COHERE_API_KEY,
    LAPTOP_DB,
    LAPTOP_PAYLOADS,
    LAPTOP_VECTORS,
    LAPTOPS_COLLECTION_NAME,
    QDRANT_BATCH_SIZE,
    QDRANT_INIT_KWARGS,
)

cohere = CohereClient(COHERE_API_KEY)
qdrant = QdrantClient(**QDRANT_INIT_KWARGS)
console = get_console()


def embed_laptops() -> None:
    """Embed all laptop classifications."""
    payloads: list[list[str]] = []
    embeddings: list[list[float]] = []
    data: list[dict] = json.loads(LAPTOP_DB.read_text())

    for laptop in data[:]:
        _payloads = []
        for datapoint in ("name", "mpn", "info", "description"):
            _payloads.append(laptop[datapoint])
        _payloads.append(
                classify_laptop_price(laptop["prices"]))
        payloads.append(" ".join(_payloads))

    batch_counter = 1
    payload_size = len(payloads)
    no_of_batches, r = divmod(payload_size, 96)
    if r != 0:
        no_of_batches += 1
    batch: list = []
    for payload in payloads:
        batch.append(payload)
        if len(batch) >= 96:
            console.log(f"Embedding batch {batch_counter} of {no_of_batches}...")
            resp = cohere.embed(batch, model="multilingual-22-12")
            embeddings.append(resp.embeddings)
            batch_counter += 1
            batch = []
    if len(batch) > 0:
        console.log(f"Embedding batch {batch_counter} of {no_of_batches}...")
        resp = cohere.embed(batch, model="multilingual-22-12")
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
    console.log(f"Creating collection {LAPTOPS_COLLECTION_NAME!r}...")
    qdrant.recreate_collection(
        collection_name=LAPTOPS_COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    # upload collection
    console.log(f"Uploading collection {LAPTOPS_COLLECTION_NAME!r}...")
    qdrant.upload_collection(
        collection_name=LAPTOPS_COLLECTION_NAME,
        vectors=vectors,
        payload=data,
        ids=[laptop["id"] for laptop in data],
        batch_size=QDRANT_BATCH_SIZE,
        parallel=10,
    )
    console.log("Done ✔")


def classify_laptop_price(prices) -> str:
    """
    Classify laptop price.

    Args:
        prices: the list of prices to classify
    Returns:
        The classification
    """
    if not prices:
        return "This laptop is mid-range."

    price_values = []
    for price in prices:
        price_value = price.get("price")
        if price_value:
            price_values.append(float(price_value))

    if not price_values:
        return "No price information available."

    avg_price = sum(price_values) / len(price_values)
    if avg_price < 500:
        return "This laptop is very affordable."
    elif avg_price < 1000:
        return "This laptop is moderately priced."
    else:
        return "This laptop is expensive."


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
        self.data = json.loads(LAPTOP_DB.read_text())

    def search(self, text: str, limit=5):
        """
        Query the database.

        Args:
            text: text to use to query database
        """
        # Convert text query into vector
        vector = self.model.embed([text], model="multilingual-22-12").embeddings[0]
        # print(f"Vectors: {vector}")

        # Use `vector` for search for closest vectors in the collection
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=np.array(vector),
            with_payload=False,
            query_filter=None,  # We don't want any filters for now
            limit=limit,  # 5 the most closest results is enough
        )
        # print(search_result[0])
        # print("\n---\n")
        # print(self.data[search_result[0].id])
        # `search_result` contains found vector ids with similarity
        # scores along with the stored payload
        # In this function we are interested in payload only
        payloads = []
        for hit in search_result:
            for laptop in self.data:
                if laptop["id"] == hit.id:
                    break
            payloads.append(laptop)
        return payloads
