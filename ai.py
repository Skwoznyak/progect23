import requests
import fake_useragent
from bs4 import BeautifulSoup
import json  # Добавляем импорт
num = input()
session = requests.Session()
link = 'https://www.cargog20.com/jeecg-boot/appHandle/queryByBillNo'

user = fake_useragent.UserAgent().random
header = {'user-agent': user}

data = {
    'waybillNo': num,
}

responce = session.post(link, json=data, headers=header).text

# Получаем totalWeight из JSON-ответа
try:
    responce_json = json.loads(responce)
    waybill_detail = responce_json.get('result', {}).get('waybillDetail', {})
    trace_list = responce_json.get('result', {}).get('traceList', [])

    total_weight = waybill_detail.get('totalWeight')
    total_volume = waybill_detail.get('totalVolume')

    
    if trace_list:
        last_stage = trace_list[0] 
        stage_status = last_stage.get('distance')
        stage_date = last_stage.get('locateTime')
    else:
        stage_status = None
        stage_date = None

    print('Вес посылки:', total_weight)
    print('Объем посылки:', total_volume)
    print('Этап посылки:', stage_status)
    print('Дата актуализации:', stage_date)
except Exception as e:
    print('Ошибка при разборе ответа:', e)