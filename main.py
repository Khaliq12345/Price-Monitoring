import requests
from bs4 import BeautifulSoup
from pony import orm
from datetime import datetime
from latest_user_agents import get_random_user_agent
import json

db = orm.Database()
db.bind(provider='sqlite', filename='products.db', create_db=True)

class Product(db.Entity):
    name = orm.Required(str)
    price = orm.Required(float)
    created_date = orm.Required(datetime)

db.generate_mapping(create_tables=True)

def gear4(session):
    url = 'https://www.gear4music.com/Guitar-and-Bass/VISIONSTRING-Electric-Guitar-Pack-Red/5B1K'
    resp = session.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    data = (
        'gears4music',
        float(soup.select_one('meta[itemprop="price"]')['content']),
    )

    return data

def guitarsrebellion(session):
    url = 'https://www.guitarsrebellion.com/collections/cornerstone-music-gear/products/cornerstone-aquarium-univibe'
    resp = session.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    json_data = soup.select_one('textarea[aria-label="Product JSON"]').text
    json_data = json.loads(json_data)
    data = (
        'guitarsrebellion',
        float(json_data[0]['price']),
    )

    return data

def musicgear(session):
    url = 'https://www.musicgear.me/product/korg-pa5x-61-keys/'
    resp = session.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    json_data = soup.select('script[type="application/ld+json"]')[-1].text
    json_data = json.loads(json_data)
    data = (
        'musicgear',
        float(json_data['@graph'][1]['offers'][0]['price']),
    )

    return data

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': get_random_user_agent()
    })

    data = [
        gear4(session),
        guitarsrebellion(session),
        musicgear(session),
    ]

    with orm.db_session:
        for item in data:
            Product(name=item[0], price=item[1], created_date=datetime.now())

if __name__ == '__main__':
    main()