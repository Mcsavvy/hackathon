from qdrant_client import QdrantClient
import os
import cohere
from typing import Sequence
from cohere.embeddings import Embeddings, Embedding
import numpy as np
import json

co = cohere.Client(os.getenv("COHERE_API_KEY"))

qd = QdrantClient(
    host=os.getenv("QDRANT_HOST"), 
    api_key=os.getenv("QDRANT_API_KEY"),
)

def create_embeddings(texts: list[str]) -> np.ndarray[float]:
    """
    Creates embeddings from a list of strings. The length of
    returned list of embeddings corresponds with the length
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
