"""
Populate Database.

This file contains functionalities used to populate the database.
NOTE: this population is temporary and would be used until we find
a valid source.
"""

import asyncio
import json
import os
from urllib.parse import urlparse, urlunparse

import aiohttp
import requests
from requests.exceptions import RequestException

LAPTOPS_API_ENDPOINT = "https://api.device-specs.io/api/laptops/"
PHONES_API_ENDPOINT = "https://api.device-specs.io/api/smartphones/"
headers = {"Authorization": f"bearer {os.environ['DEVICESPECS_API_KEY']}"}


async def get_pagination(session, url: str) -> int:
    """
    Find out how many pages you need to go through.

    Args:
        session: aiohttp client session object
        url: the url of the api
    Returns:
        the number of pages in the API
    """
    async with session.get(url, headers=headers) as response:
        if not response.ok:
            raise aiohttp.ClientError(f"{response.reason}")
        response = await response.json()
        pagination = response["meta"]["pagination"]
        return pagination["pageCount"]


async def get_laptop(session, url):
    """Fetch details of a single laptop."""
    async with session.get(url, headers=headers) as response:
        if not response.ok:
            raise aiohttp.ClientError(f"Request failed with status {response.status}")
        data = await response.json()
        return data["data"]


async def get_laptops(session: aiohttp.ClientSession) -> None:
    """Get all laptops from API and save to file."""
    async with aiohttp.ClientSession() as session:
        # Get total number of pages
        pages = await get_pagination(session, LAPTOPS_API_ENDPOINT)

        # Prepare query string for API endpoint
        parsed_url = urlparse(LAPTOPS_API_ENDPOINT)
        query = parsed_url.query
        if query:
            query += "&"

        # Fetch laptop data for all pages
        laptops = []
        tasks = []
        for page in range(1, pages + 1):
            print(f"Page {page} of {pages}:\n{'-' * 16}")
            url = urlunparse(
                (
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    query + f"pagination[page]={page}",
                    parsed_url.fragment,
                )
            )
            async with session.get(url, headers=headers) as response:
                if not response.ok:
                    raise aiohttp.ClientError(
                        f"Request failed with status {response.status}"
                    )
                page_data = await response.json()

            # Fetch laptop details for each laptop in page asynchronously
            for count, laptop in enumerate(page_data["data"], start=1):
                print(f"[x] Laptop {count}")
                laptop_url = urlunparse(
                    (
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path + f"{laptop['id']}",
                        parsed_url.params,
                        query + "populate=*",
                        parsed_url.fragment,
                    )
                )
                tasks.append(asyncio.ensure_future(get_laptop(session, laptop_url)))

            # Wait for all laptop details to be fetched
            # before continuing to next page
            laptops += await asyncio.gather(*tasks)
            tasks = []

            print()

        # Save laptop data to file
        with open("json_files/laptops_raw.json", "w+") as db:
            json.dump(laptops, db)


async def get_phone(session, url):
    """Fetch details of a single laptop."""
    async with session.get(url, headers=headers) as response:
        if not response.ok:
            raise aiohttp.ClientError(f"Request failed with status {response.status}")
        data = await response.json()
        return await data["data"]


async def get_phones(session: aiohttp.ClientSession) -> None:
    """Get all phones from API and save to file."""
    async with aiohttp.ClientSession() as session:
        # Get total number of pages
        pages = await get_pagination(session, PHONES_API_ENDPOINT)

        parsed_url = urlparse(PHONES_API_ENDPOINT)
        query = parsed_url.query
        if query:
            query += "&"
        phones: list[dict] = []
        tasks = []
        for page in range(1, pages + 1):
            # Page 2019 of 2020:
            print(f"Page {page} of {pages}:\n{'-' * 16}")
            url = urlunparse(
                (
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    query + f"pagination[page]={page}",
                    parsed_url.fragment,
                )
            )
            async with session.get(url, headers=headers) as response:
                if not response.ok:
                    raise aiohttp.ClientError(
                        f"Request failed with status {response.status}"
                    )
                page_data = await response.json()
            for count, obj in enumerate(page_data["data"], start=1):
                id: int = obj["id"]
                print(f"[x] Phone {count}")
                phone_url = urlunparse(
                    (
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path + f"{id}",
                        parsed_url.params,
                        query + "populate=*",
                        parsed_url.fragment,
                    )
                )
                tasks.append(asyncio.ensure_future(get_laptop(session, phone_url)))

            # Wait for all laptop details to be fetched
            # before continuing to next page
            phones += await asyncio.gather(*tasks)
            tasks = []

            print()

        # Save phone data to file
        with open("json_files/phones_raw.json", "w+") as db:
            json.dump(phones, db)


async def main():
    """Start main loop."""
    async with aiohttp.ClientSession(headers=headers) as session:
        print(session.headers)
        await get_laptops(session)
        await get_phones(session)


asyncio.run(main())
