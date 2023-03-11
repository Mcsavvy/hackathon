import requests
import bs4
import json

def arrange_phone_data(phone) -> dict:
    """This function arranges and serializes the phone data
gotten from the scraper. it turns it into a dictionary"""
    short_desc = phone.get_text()
    img = "https://phonedb.net/" + str(phone.select_one('a>img').get("src"))
    temp = short_desc.split('\n')
    phone_dict = {}
    phone_dict.update(name=temp[1])
    phone_dict.update(image=img)
    phone_dict.update(description=temp[-1])
    return phone_dict

link = "https://phonedb.net/index.php?m=device&s=list"
def get_all_phones(link):
    """This function gets all the relevant data from a page"""
    resp = requests.get(link)
    soup = bs4.BeautifulSoup(resp.text, features="html.parser")
    text = soup.find_all("div", class_="content_block")
    all_phone_data = []
    try:
        for index, value in enumerate(text):
            b = arrange_phone_data(value)
            all_phone_data.append(b)
    except:
        pass
    return all_phone_data

def get_next_link(link: str):
    resp = requests.get(link)
    soup = bs4.BeautifulSoup(resp.text, features="html.parser")
    text = soup.select_one("div.container > a[title='Next page']")
    if not text:
        return None
    url = "https://phonedb.net" + str(text['href'])
    # print(url)
    return url
def serialize_db(link):
    """This function serializes the whole result of the scraper.
It converts it to json format and then writes the result
to the file scraper.py"""
    final = []
    while True:
        url = link
        if not url:
            break;
        page = get_all_phones(url)
        final.append(page)
        link = get_next_link(url)
    end_result = []
    for page in final:
        for phone in page:
            end_result.append(phone)
    with open("phones.json", 'w') as fd:
        json.dump(end_result, fd)
    # print(end_result)

if __name__ == '__main__':
    serialize_db(link)
