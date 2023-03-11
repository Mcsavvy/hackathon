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

import cohere
import numpy as np
import pandas as pd
from cohere.embeddings import Embeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse
from tqdm import tqdm

PAYLOAD_FILE = "startups.json"
VECTORS_FILE = "startups.npy"
BATCH_SIZE = 256
COLLECTION_NAME = "startups"

co = cohere.Client(os.getenv("COHERE_API_KEY"))
qd = QdrantClient(
    host=os.getenv("QDRANT_HOST"),
    api_key=os.getenv("QDRANT_API_KEY"),
)


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
    batch: list[str] = []
    for text in texts:
        batch.append(text)
        if len(batch) >= batch_size:
            response = co.embed(batch)
            for embedding in response.embeddings:
                embeddings.append(embedding)
            batch = []
    if len(batch) > 0:
        response = co.embed(batch)
        for embedding in response.embeddings:
            embeddings.append(embedding)
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
        description = row.alt + ". " + row.description
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
    vector_size = 768
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
        batch_size=BATCH_SIZE  # How many vectors will be uploaded at once?
    )


if __name__ == "__main__":
    if not os.path.isfile(PAYLOAD_FILE):
        print(f"Payload file {PAYLOAD_FILE} doesn't exist!", file=sys.stderr)
        exit(1)

    if os.path.isfile(VECTORS_FILE):
        print(f"Embeddings already exists.")
    else:
        print(f"Creating embeddings...")
        embed_payload()

    try:
        qd.get_collection(COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME!r} already exists.")
        create_collection("startups")
    except UnexpectedResponse as exc:
        if exc.status_code == 404:
            print(f"Creating collection {COLLECTION_NAME!r}...")
            create_collection("startups")
        else:
            raise