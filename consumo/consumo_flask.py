from flask import Flask, request, jsonify
from datetime import datetime
import joblib
import numpy as np

app = Flask(__name__)

# Taxa de emissão de CO₂ em kg/kWh
CO2_EMISSION_RATE = 0.233  # Ajuste conforme necessário

# Carregar o modelo de IA treinado
model = joblib.load('energy_consumption_model.pkl')

@app.route('/calculateLamp', methods=['POST'])
def calculate():
    try:
        # Receber o consumo do dispositivo em watts
        device_power_watts = request.json.get('device_power', 0)  # Em watts
        logs = request.json.get('logs', [])

        if device_power_watts <= 0:
            return jsonify({'error': 'Device power must be greater than zero'}), 400

        # Ordenar os logs pela data
        logs = sorted(logs, key=lambda x: datetime.strptime(x.get('timeStr'), "%Y-%m-%d %H:%M:%S"))

        energy_per_hour = device_power_watts / 1000  # Convertendo watts para kWh

        daily_energy = {}
        weekly_energy = {}
        monthly_energy = {}

        previous_time = None
        total_energy = 0

        # Iterar sobre os logs para calcular o tempo em que o dispositivo ficou ligado
        for log in logs:
            timestamp = log.get('timeStamp')
            value = log.get('value')
            time_str = log.get('timeStr')

            log_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            if previous_time is not None:
                # Calcular a diferença de tempo entre os logs de ligar/desligar
                time_diff = (log_time - previous_time).total_seconds() / 3600.0  # Em horas

                if value == "false":  # Se o valor for "false", o dispositivo estava desligado
                    energy_consumed = time_diff * energy_per_hour

                    # Atualizar a energia total
                    total_energy += energy_consumed

                    # Atualizar o consumo por dia, semana e mês
                    day = log_time.date()
                    week = log_time.isocalendar()[1]
                    month = log_time.month

                    # Consumo diário
                    if day not in daily_energy:
                        daily_energy[day] = 0
                    daily_energy[day] += energy_consumed

                    # Consumo semanal
                    if week not in weekly_energy:
                        weekly_energy[week] = 0
                    weekly_energy[week] += energy_consumed

                    # Consumo mensal
                    if month not in monthly_energy:
                        monthly_energy[month] = 0
                    monthly_energy[month] += energy_consumed

            # Atualizar o tempo anterior somente se o valor for "true" (ligado)
            if value == "true":
                previous_time = log_time

        # Calcula a pegada de carbono
        carbon_footprint = total_energy * CO2_EMISSION_RATE

        # Convertendo as chaves dos dicionários de datetime.date para strings
        daily_energy_str = {str(day): value for day, value in daily_energy.items()}
        weekly_energy_str = {str(week): value for week, value in weekly_energy.items()}
        monthly_energy_str = {str(month): value for month, value in monthly_energy.items()}

        # Retornar os valores de consumo e pegada de carbono para o Flutter
        return jsonify({
            'daily_energy': daily_energy_str,
            'weekly_energy': weekly_energy_str,
            'monthly_energy': monthly_energy_str,
            'total_energy': total_energy,
            'carbon_footprint': carbon_footprint
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predictLamp', methods=['POST'])
def predict():
    try:

        # Receber a potência do dispositivo e os logs

        device_power_watts = request.json.get('device_power', 0)

        logs = request.json.get('logs', [])

        if device_power_watts <= 0:
            return jsonify({'error': 'Device power must be greater than zero'}), 400

        # Ordenar os logs pela data

        logs = sorted(logs, key=lambda x: datetime.strptime(x.get('timeStr'), "%Y-%m-%d %H:%M:%S"))

        previous_time = None

        total_usage_hours = 0

        # Iterar sobre os logs para calcular o tempo total de uso

        for log in logs:

            time_str = log.get('timeStr')

            value = log.get('value')

            log_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            if previous_time is not None:

                time_diff = (log_time - previous_time).total_seconds() / 3600.0  # Em horas

                if value == "false":
                    total_usage_hours += time_diff

            if value == "true":
                previous_time = log_time

        # Fazer a predição do consumo mensal usando o modelo treinado

        predicted_energy_kwh = model.predict([[device_power_watts, total_usage_hours]])[0]

        # Calcular a pegada de carbono prevista

        predicted_carbon_footprint = predicted_energy_kwh * CO2_EMISSION_RATE

        # Retornar os valores previstos

        return jsonify({

            'predicted_monthly_energy': predicted_energy_kwh,

            'predicted_carbon_footprint': predicted_carbon_footprint

        })


    except Exception as e:

        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
