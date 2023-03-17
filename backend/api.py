"""This module contains two major functions, our run funtion which
is basically a wrapper function for our searcher and a fast api
which broadcasts our information."""

from flask import Flask, jsonify
from .laptops.embed_laptops import NeuralSearcher
from .config import LAPTOPS_COLLECTION_NAME


app = Flask(__name__)
searcher = NeuralSearcher(LAPTOPS_COLLECTION_NAME)

@app.route('/search/<query>', methods=['GET'])
def search(query):
    return jsonify({'recommendations': searcher.search(query)})

if __name__ == '__main__':
    app.run(debug=True)

