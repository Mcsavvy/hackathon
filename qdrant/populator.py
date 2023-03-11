"""
Populate Database.

This file contains functionalities used to populate the database.
NOTE: this population is temporary and would be used until we find
a valid source.
"""

import requests
import bs4
import os
import json
from typing import TypedDict


LAPTOPS_API_ENDPOINT = "https://api.device-specs.io/api/laptops/?populate=*"
PHONES_API_ENDPOINT = "https://api.device-specs.io/api/smartphones?populate=*"


session = requests.session()
session.headers.update({
    "Authorization": f"bearer {os.environ['DEVICESPECS_API_KEY']}"
})


class Laptop(TypedDict):
    """Dictionary representation of a laptop entry."""

    id: int
    name: str
    model: str
    images: list[str]
    url: str
    price: tuple[str, float, float]
    cpu_type: str
    cpu_implementation: str
    cpu_cores: int
    display_size: float
    memory: float
    storage_type: str
    storage: float
    color: str


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


def get_laptop(data: dict) -> Laptop:
    """
    Clean the data returned from the API call.

    This function cleans up the data returned and works with
    only what is neccessary.

    Args:
        data: the data returned from the API search
    Returns:
        a sanitized version of the input data
    """
    laptop = Laptop()  # type: ignore
    laptop["id"] = data.get("id")
    laptop["name"] = data.get("name")
    laptop["model"] = data.get("mpn")
    laptop["images"] = [image["url"] for image in data.get("images", ())]
    if data["prices"]:
        laptop["url"] = data["prices"][0]["url"]
        laptop["price"] = (
            data["prices"][0].get("currency", "USD"),
            data["prices"][0].get("old_price", 0),
            data["prices"][0].get("price", 0)
        )
    else:
        laptop["url"] = None
        laptop["price"] = ("USD", 0, 0)
    laptop["cpu_type"] = data["main"].get("cpu_type")
    laptop["cpu_implementation"] = data["main"].get("cpu_implementation", None)
    laptop["display_size"] = data["main"].get("display_size__inch", 0)
    laptop["memory"] = data["main"].get("memory_ram__gb", 0)
    laptop["storage_type"] = data["main"].get("storage_type", None)
    laptop["storage"] = data["main"].get("storage_capacity__gb", 0)
    laptop["color"] = data["main"].get("design_color_name", None)
    return laptop


def get_laptops():
    """Get all laptops from API."""
    pages = get_pagination(LAPTOPS_API_ENDPOINT)
    laptops = list[Laptop]()
    for page in range(1, pages + 1):
        response = session.get(
            f"{LAPTOPS_API_ENDPOINT}&pagination[page]={page}")
        for data in response.json()["data"]:
            laptops.append(get_laptop(data))
    with open("laptops.json", "w+") as db:
        json.dump(laptops, db)


get_laptops()
