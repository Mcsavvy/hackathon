"""This module contains two major functions, our run funtion which
is basically a wrapper function for our searcher and a fast api
which broadcasts our information."""

from flask import Flask, jsonify, request
from .laptops.embed_laptops import NeuralSearcher
from .config import LAPTOPS_COLLECTION_NAME
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
searcher = NeuralSearcher(LAPTOPS_COLLECTION_NAME)

@app.route('/search/<query>', methods=['GET'])
def search(query):
    limit = request.args.get("limit", 5)
    limit = int(limit)
    return jsonify({
        'recommendations': searcher.search(query, limit=limit)
    })
