import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
import json
import os


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
    # Exemplo de dados simulados
    simulated_data = [
        {"date": "2024-09-01 00:00:00.000", "totalCoust": 8.61},
        {"date": "2024-08-01 00:00:00.000", "totalCoust": 9.32},
        {"date": "2024-07-01 00:00:00.000", "totalCoust": 7.25},
    ]

    # Salvando os dados simulados em um arquivo JSON
    with open('plug_data.json', 'w') as f:
        json.dump(simulated_data, f, indent=4)

    # Treinando o modelo
    train_model()
