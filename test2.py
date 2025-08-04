import requests
import fake_useragent
from bs4 import BeautifulSoup

session = requests.Session()
link = 'https://www.cargog20.com/jeecg-boot/appHandle/queryByBillNo'

user = fake_useragent.UserAgent().random
header = {'user-agent': user}

data = {
    'waybillNo': '1BUYBOX3876-0719-2-1'
}

responce = session.post(link, json=data, headers=header).text
print(responce)


cookies_dict = [
    {'domain': key.domain, 'name': key.name, 'value': key.value}
    for key in session.cookies
]
