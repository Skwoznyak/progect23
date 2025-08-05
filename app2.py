from flask import Flask, request, jsonify
import requests
import fake_useragent

app = Flask(__name__)

# Создаём объект UserAgent один раз
try:
    ua = fake_useragent.UserAgent()
    header = {'user-agent': ua.random}
except Exception as e:
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}

@app.route('/track', methods=['POST'])
def track_package():
    try:
        # Пробуем получить данные из JSON
        data = request.get_json()
        if data and 'waybillNo' in data:
            waybill_no = data['waybillNo']
        # Если JSON пуст, пробуем взять из формы
        elif request.form and 'waybillNo' in request.form:
            waybill_no = request.form['waybillNo']
        else:
            return jsonify({"error": "Трек-номер не указан"}), 400

        # Запрос к внешнему API
        link = 'https://www.cargog20.com/jeecg-boot/appHandle/queryByBillNo'
        payload = {'waybillNo': waybill_no}
        response = requests.post(link, json=payload, headers=header, timeout=10)
        response.raise_for_status()  # Проверяем успешность
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

        # Формируем ответ
        result = {
            "status": "success",
            "data": {
                "waybillNo": waybill_no,
                "totalWeight": total_weight,
                "totalVolume": total_volume,
                "stageStatus": stage_status,
                "stageDate": stage_date
            }
        }
        return jsonify(result), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Ошибка подключения: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)