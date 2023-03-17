# Project Title

Salesman: A Multilingual Semantic Search Vectors Gadgets Recommendation Application

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](/LICENSE)

## Project Description

Salesman is a gadgets recommendation application that uses multilingual semantic search vectors to help users find the perfect gadgets for their needs. The application allows users to input their desired specifications and preferences, and returns a list of laptops that match those criteria. Salesman uses advanced AI and machine learning algorithms to provide accurate and personalized laptop recommendations to users.

## Installation

To install Salesman, follow these steps:
> NOTE: You would need to have python version 3.10 upwards installed.

```sh
git clone https://github.com/mcsavvy/salesman.git
cd salesman
pipenv install
```

## Usage

### From The Commandline

```sh
pipenv run salesman interactive

# limit the number of output (default: 5)

pipenv run salesman interactive --limit 10

# produce output in json format

pipenv run salesman interactive --json
```

### To Serve API

```sh
pipenv run salesman web

# You can optionally specify host and port

pipenv run salesman web --host 0.0.0.0 --port 80
```


## Contributing

If you would like to contribute to Salesman, please go through [this](/Contributing.md) first.


## License

Salesman is licensed under the **MIT** license. See the [licence](/LICENSE) file for more information.

## Contact

If you have any questions or concerns about Salesman, please contact any of the developers.

- [Uguwanyi Afam](mailto:phyrokelstein@gmail.com)
- [Kasiemobi](/)
- [Emmanuel Myles](mailto:cyrile450@gmail.com)
- [Dave Mcsavvy](mailto:davemcsavvii@gmail.com)

## Tools Used

### Cohere
We used [Cohere](https://cohere.ai/) to do a series of tasks:

- To classify gadgets. Check [here](/classifications.md) to see what and what was classified.

- To summarize different details of a gadget into one complete paragraph.

- To embed payloads.

- To embed queries.


### Qdrant
We used [Qdrant](http://qdrant.tech/) in the following ways:

- **Qdrant** acted as a host for our embeddings and also the payload data.

- **Qdrant** also did vector search and filtering based on queries.

### Flask
[Flask](https://flask.palletsprojects.com/) was used to serve our api.

### Rich
[Rich](https://rich.readthedocs.io/en/latest/) was used to display colorful content and beautiful layouts of data in the terminal.

### Click
[Click](https://click.palletsprojects.com/en) was used to create the amazing commandline interface.

### Requests & Aiohttp
For the initial fetching of data [Requests](https://requests.readthedocs.io/) came to the rescue. However, as we needed to go faster, we had to use [Aiohttp](https://docs.aiohttp.org/)