from flask import Flask, request
import requests
import fake_useragent

app = Flask(__name__)

# Создаём объект UserAgent один раз при старте
try:
    ua = fake_useragent.UserAgent()
except Exception as e:
    # Запасной User-Agent, если fake_useragent не сработал
    ua = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}


@app.route('/track', methods=['POST'])
def track_package():
    try:
        # Получаем трек-номер из JSON-запроса
        data = request.get_json()
        num = data.get('waybillNo')
        if not num:
            return "Трек-номер не указан", 400

        session = requests.Session()
        link = 'https://www.cargog20.com/jeecg-boot/appHandle/queryByBillNo'

        try:
            header = {'user-agent': ua.random}
        except:
            header = {'user-agent': ua['user-agent']}

        payload = {'waybillNo': num}

        response = session.post(link, json=payload, headers=header)
        response.raise_for_status()  # Проверяем, что запрос успешен
        response_json = response.json()

        # Извлекаем данные
        waybill_detail = response_json.get(
            'result', {}).get('waybillDetail', {})
        trace_list = response_json.get('result', {}).get('traceList', [])

        total_weight = waybill_detail.get('totalWeight', 'Не указан')
        total_volume = waybill_detail.get('totalVolume', 'Не указан')

        if trace_list:
            last_stage = trace_list[0]
            stage_status = last_stage.get('distance', 'Не указан')
            stage_date = last_stage.get('locateTime', 'Не указана')
        else:
            stage_status = 'Информация отсутствует'
            stage_date = 'Информация отсутствует'

        # Формируем ответ в текстовом формате
        result = (
            f"Вес посылки: {total_weight}\n"
            f"Объем посылки: {total_volume}\n"
            f"Этап посылки: {stage_status}\n"
            f"Дата актуализации: {stage_date}"
        )
        return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        return f"Ошибка: {str(e)}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
