from flask import Flask, jsonify, request
import time

app = Flask(__name__)
precip_per_day = 0.0

@app.route('/onecall', methods=['GET'])
def onecall():
    daily_data = []
    for i in range(10):
        day_data = {
            "dt": int(time.time()) + i * 86400,
            "rain": precip_per_day
        }
        daily_data.append(day_data)

    response = {
        "lat": 33.44,
        "lon": -94.04,
        "timezone": "America/Chicago",
        "timezone_offset": -18000,
        "daily": daily_data
    }

    print(f"📤 Enviando resposta com {precip_per_day} mm/dia para 10 dias")
    return jsonify(response)

@app.route('/set', methods=['POST'])
def set_precip():
    global precip_per_day
    value = request.args.get('value')
    if value is None:
        return jsonify({"error": "Faltou o parâmetro ?value=XX"}), 400
    try:
        precip_per_day = float(value)
        print(f"✅ Valor atualizado para {precip_per_day} mm/dia")
        return jsonify({"message": f"Chuva atualizada para {precip_per_day} mm/dia"})
    except ValueError:
        return jsonify({"error": "Valor inválido, use número."}), 400

if __name__ == '__main__':
    print("✅ Servidor rodando em http://localhost:5050")
    print("📌 Use: curl -X POST http://localhost:5050/set?value=12.3")
    print("📌 Ou abra: http://localhost:5050/onecall")
    app.run(host="0.0.0.0", port=5050)
