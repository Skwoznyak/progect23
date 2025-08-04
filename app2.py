from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import fake_useragent

app = Flask(__name__)
CORS(app)  # Включаем CORS для работы с ботами

# Создаём объект UserAgent один раз при старте
try:
    ua = fake_useragent.UserAgent()
except Exception as e:
    ua = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

@app.route('/track', methods=['POST'])
def track_package():
    try:
        # Получаем трек-номер из JSON-запроса
        data = request.get_json()
        num = data.get('waybillNo')
        if not num:
            return jsonify({"error": "Трек-номер не указан"}), 400

        session = requests.Session()
        link = 'https://www.cargog20.com/jeecg-boot/appHandle/queryByBillNo'

        try:
            header = {'user-agent': ua.random}
        except:
            header = {'user-agent': ua['user-agent']}

        payload = {'waybillNo': num}
        response = session.post(link, json=payload, headers=header, timeout=10)
        response.raise_for_status()  # Проверяем, что запрос успешен
        response_json = response.json()

        # Извлекаем данные
        waybill_detail = response_json.get('result', {}).get('waybillDetail', {})
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

        # Формируем JSON-ответ
        result = {
            "status": "success",
            "data": {
                "waybillNo": num,
                "totalWeight": total_weight,
                "totalVolume": total_volume,
                "stageStatus": stage_status,
                "stageDate": stage_date
            }
        }
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)