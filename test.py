import requests
import fake_useragent
from bs4 import BeautifulSoup


user = fake_useragent.UserAgent().random
header= {'user-agent': user}

link = ''
link2 = 'https://browser-info.ru/'
responce =  requests.get(link2, headers=header).text
soup = BeautifulSoup(responce, 'lxml')
block = soup.find('div', id="tool_padding")

check_js = block.find('div', id='javascript_check')
res_js = check_js.find_all('span')[1].text

block2 = soup.find('div', id='tool_padding')
check_flesh = block2.find('div', id='flash_version')
res_flesh = check_flesh.find_all('span')[1].text


check_user = block.find('div', id='user_agent').text
print(check_user)