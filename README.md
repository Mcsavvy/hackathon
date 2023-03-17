# HACKATHON

We learned and implemented Co:here and qdrant for the lablab ai hackthon

# FILES

[backend](https://github.com/Mcsavvy/hackathon/tree/main/backend)
[salesman](https://github.com/Mcsavvy/hackathon/tree/main/salesman)
[.gitignore](https://github.com/Mcsavvy/hackathon/tree/main/.gitignore)
[Pipfile](https://github.com/Mcsavvy/hackathon/tree/main/Pipfile)
[Pipfile.lock](https://github.com/Mcsavvy/hackathon/tree/main/Pipfile.lock)
[__init__.py](https://github.com/Mcsavvy/hackathon/tree/main/__init__.py)
[classifications.md](https://github.com/Mcsavvy/hackathon/tree/main/classifications.md)
[requirements.txt](https://github.com/Mcsavvy/hackathon/tree/main/requirements.txt)


# DESCRIPTION
This is a **Gadget Communication Finder** called ***Salesman***. ***Salesman*** takes in a description of a gadget and gives the user products/gadgets according to the description given.

# HOW WE HANDLED OUR DATA

## Web scraping
We scraped out data from site's that sells these gadgets to use in our software.

## API
But the data we scraped didn't seem complete, So we used an [API](https://github.com/Mcsavvy/hackathon/blob/main/backend/api.py) to generate.

## CLASSIFY DATA
After getting all the details we need, We then trained and wrote classifications and descriptions with **cohere** to train our model to give meaningful responses suitable for different users **e.g**: Sudents, Business owners etc...
For more info ceck check out:
[classifications.md](https://github.com/Mcsavvy/hackathon/blob/main/classifications.md)


## EMNBEDDING DATA
.....

## SCHEMAS
We created [schemas](https://github.com/Mcsavvy/hackathon/tree/main/backend/schemas) to give us a better layout of what the data looks like.

## PRICE
The prices were in USD/EUR, we needed just USD so we converted the EUR to USD.
See [converter.py](https://github.com/Mcsavvy/hackathon/blob/main/backend/database/currency_converter.py)