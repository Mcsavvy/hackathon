"""This module contains two major functions, our run funtion which
is basically a wrapper function for our searcher and a fast api
which broadcasts our information."""
from fastapi import FastAPI
import uvicorn
from backend.neural_search import NeuralSearcher
from backend.generate_response import interpret
import search_bar


def run(query):
    """This takes a query and searches it with the aid of our neural searcher
It then converts the information into a user friendly message useing our interpret
function and then returns a json response consisting of image and description pairs"""
    results = search_bar.search(query)
    response = []
    for result in results:
        temp_dict = {}
        message = interpret(result)
        temp_dict.update(description=message)
        temp_dict.update(images=result['img'])
        response.append(result)
    return response


salesman = FastAPI()
@salesman.get('/salesman/{query}')
async def perfect_salesman():
    return {"recommendations": run(query)}

if __name__ == '__main__':
    uvicorn.run(salesman, host='127.0.0.1', port='8000')