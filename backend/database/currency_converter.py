from ..config import LAPTOP_DB
import json

"""
'currency': {
                'count': 8435,
                'type': 'string',
                'values': ['EUR', 'USD']
            },
            'url': {'count': 8435, 'type': 'string'}

"""

"""
Data(list):
    Laptop(dict):
        prices(list) -> PRICE OLDPRICE currency
"""
def cur_converter():
    with open(LAPTOP_DB, "r") as f:
        data = json.loads(f.read())
        for laptop in data:
            for prices in laptop["prices"]:
                if (prices["price"] != None) and (prices["old_price"] != None):
                    if prices["currency"] == "EUR":
                        prices["price"] += 0.01
                        prices["old_price"] += 0.01
                        prices["currency"] = "USD"

                else:
                    if (prices["price"] == None) and (prices["old_price"] != None):
                        prices["price"] = prices["old_price"] / 2
                    elif (prices["price"] != None) and (prices["old_price"] == None):
                        prices["old_price"] = prices["price"] * 2
                    else:
                        prices["price"] = 200
                        prices["old_price"] = 400
                    prices["currency"] = "USD"

    with open(LAPTOP_DB, "w") as f:
        f.write(json.dumps(data))

if __name__ == "__main__":
    cur_converter()
