from flask import Flask, request, jsonify
from datetime import datetime
import joblib
import numpy as np

app = Flask(__name__)

# Taxa de emissão de CO₂ em kg/kWh
CO2_EMISSION_RATE = 0.233  # Ajuste conforme necessário

# Carregar o modelo de IA treinado
model = joblib.load('energy_consumption_model_plug.pkl')

@app.route('/calculatePlug', methods=['POST'])
def calculate():
    try:
        # Receber os dados do dispositivo
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extrair o total de consumo
        total_consumption = float(data.get('total', 0))

        # Se o total de consumo for inválido
        if total_consumption <= 0:
            return jsonify({'error': 'Total consumption must be greater than zero'}), 400

        # Calcular a pegada de carbono
        carbon_footprint = total_consumption * CO2_EMISSION_RATE

        # Retornar os valores de consumo e pegada de carbono
        return jsonify({
            'total_energy': total_consumption,
            'carbon_footprint': carbon_footprint
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predictPlug', methods=['POST'])
def predict():
    try:
        # Receber os dados do dispositivo
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extrair o total de consumo
        total_consumption = float(data.get('total', 0))

        if total_consumption <= 0:
            return jsonify({'error': 'Total consumption must be greater than zero'}), 400

        # Fazer a predição usando o modelo treinado
        predicted_energy_kwh = model.predict([[total_consumption]])[0]

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
