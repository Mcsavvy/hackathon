"""This module contains two major functions, our run funtion which
is basically a wrapper function for our searcher and a fast api
which broadcasts our information."""
import uvicorn
from fastapi import FastAPI

from .config import LAPTOPS_COLLECTION_NAME
from .laptops.embed_laptops import NeuralSearcher


def run(query):
    """This takes a query and searches it with the aid of our neural searcher
    It then converts the information into a user friendly message useing our interpret
    function and then returns a json response consisting of image and description pairs
    """
    results = search_bar.search(query)
    response = []
    for result in results:
        temp_dict = {}
        message = interpret(result)
        temp_dict.update(description=message)
        temp_dict.update(images=result["img"])
        response.append(result)
    return response


salesman = FastAPI()
searcher = NeuralSearcher(LAPTOPS_COLLECTION_NAME)


@salesman.get("/search/{query}")
async def perfect_salesman(query):
    return {"recommendations": searcher.search(query)}
