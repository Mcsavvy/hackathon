"""
Populate Database.

This file contains functionalities used to populate the database.
NOTE: this population is temporary and would be used until we find
a valid source.
"""

import requests
import os
import json
from urllib.parse import urlparse, urlunparse
from requests.exceptions import RequestException

LAPTOPS_API_ENDPOINT = "https://api.device-specs.io/api/laptops/"
PHONES_API_ENDPOINT = "https://api.device-specs.io/api/smartphones/"


session = requests.session()
session.headers.update({
    "Authorization": f"bearer {os.environ['DEVICESPECS_API_KEY']}"
})

def get_pagination(url: str) -> int:
    """
    Find out how many pages you need to go through.
 
    Args:
        url: the url of the api
    Returns:
        the number of pages in the API
    """
    response = session.get(url)
    if not response.ok:
        raise requests.RequestException(response.reason)
    pagination = response.json()["meta"]["pagination"]
    return pagination["pageCount"]


def get_laptops():
    """Get all laptops from API."""
    pages = get_pagination(LAPTOPS_API_ENDPOINT)
    parsed_url = urlparse(LAPTOPS_API_ENDPOINT)
    query = parsed_url.query
    if query:
        query += "&"
    laptops: list[dict] = []
    for page in range(1, pages + 1):
        url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            query + f"pagination[page]={page}",
            parsed_url.fragment
        ))
        response = session.get(url)
        if not response.ok:
            raise RequestException(response.reason)
        data = response.json()["data"]
        for obj in data:
            id: int = obj["id"]
            url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path + f"{id}",
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            response = session.get(url)
            if not response.ok:
                raise RequestException(response.reason)
            laptops.append(response.json()["data"])
    with open("laptops_raw.json", "w+") as db:
        json.dump(laptops, db)

get_laptops()
