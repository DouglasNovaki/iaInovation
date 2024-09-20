import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
import json
import os
from datetime import datetime, timedelta
import random


# Função para gerar dados simulados com base em um intervalo de datas
def generate_simulated_data(start_date='2023-01-01', end_date='2024-01-01', num_records=12):
    """
    Gera um conjunto de dados simulados de consumo mensal.

    :param start_date: Data inicial no formato 'YYYY-MM-DD'
    :param end_date: Data final no formato 'YYYY-MM-DD'
    :param num_records: Número de registros a serem gerados (padrão é 12 meses)
    :return: Lista de dicionários com as informações simuladas
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Calcula a quantidade de meses entre as datas
    delta_months = (end.year - start.year) * 12 + end.month - start.month

    # Gerar consumo mensal de forma consistente
    data = []
    current_date = start

    for _ in range(min(delta_months, num_records)):
        # Simula um consumo aleatório para cada mês (por exemplo, entre 5 kWh e 15 kWh)
        total_coust = round(random.uniform(5.0, 15.0), 2)

        # Formata a data para o formato 'YYYY-MM-DD'
        data.append({
            "date": current_date.strftime('%Y-%m-%d %H:%M:%S.000'),
            "totalCoust": total_coust
        })

        # Avança para o próximo mês
        next_month = current_date.month % 12 + 1
        next_year = current_date.year + (1 if current_date.month == 12 else 0)
        current_date = current_date.replace(month=next_month, year=next_year)

    # Salvando os dados simulados em um arquivo JSON
    with open('plug_data.json', 'w') as f:
        json.dump(data, f, indent=4)

    print(f'{len(data)} registros gerados e salvos no arquivo plug_data.json.')


# Função para carregar os dados no novo formato do plug
def load_training_data(json_file='plug_data.json'):
    if not os.path.exists(json_file):
        raise FileNotFoundError(f'O arquivo {json_file} não foi encontrado.')

    with open(json_file, 'r') as f:
        data = json.load(f)

    print(f'Quantidade de registros carregados: {len(data)}')

    # Criando o DataFrame com base nos dados fornecidos
    df = pd.DataFrame(data)
    df['totalCoust'] = df['totalCoust'].astype(float)  # Convertendo o consumo total para float

    print("DataFrame final para treinamento:")
    print(df.head())

    return df


def train_model():
    df = load_training_data()

    if len(df) < 2:
        print("Não há dados suficientes para dividir em conjuntos de treinamento e teste.")
        return

    # Definindo as features (X) e o target (y)
    X = df[['totalCoust']]  # Usamos o consumo total como feature
    y = df['totalCoust']  # Nosso target também é o consumo total, mas poderíamos treinar para outros parâmetros

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    joblib.dump(model, 'energy_consumption_model_plug.pkl')
    print("Modelo de IA treinado e salvo com sucesso!")


if __name__ == "__main__":
    # Gerar dados simulados
    generate_simulated_data(start_date='2023-01-01', end_date='2023-12-01', num_records=12)

    # Treinar o modelo com os dados simulados gerados
    train_model()
