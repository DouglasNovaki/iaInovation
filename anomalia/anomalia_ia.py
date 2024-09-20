import sqlite3
import pandas as pd
import ast
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Fechar todos os plots anteriores antes de rodar o script
plt.close('all')

# Conectar ao banco de dados usando contexto para garantir o fechamento da conexão
db_path = '/Users/novaki/Documents/developer/inteligencia_artificial/device_logs.db'
with sqlite3.connect(db_path) as conn:
    # Carregar as tabelas no DataFrame
    cafeteira_log = pd.read_sql_query("SELECT * FROM CafeteiraLog", conn)
    geladeira_log = pd.read_sql_query("SELECT * FROM GeladeiraLog", conn)
    device_log = pd.read_sql_query("SELECT * FROM DeviceLog", conn)

# Função para extrair o valor de cur_voltage do campo 'status' e ajustar a escala
def extract_voltage(status_str):
    try:
        status_list = ast.literal_eval(status_str)
        voltages = [float(item['value']) / 10 for item in status_list if 'cur_voltage' in item.get('code', '')]
        timestamps = [item['t'] for item in status_list if 'cur_voltage' in item.get('code', '')]
        return voltages[0] if voltages else None, timestamps[0] if timestamps else None
    except (ValueError, SyntaxError):
        return None, None

# Aplicar a função para extrair a voltagem e o timestamp em cada log
cafeteira_log[['voltage', 'timestamp']] = cafeteira_log['status'].apply(lambda x: pd.Series(extract_voltage(x)))
geladeira_log[['voltage', 'timestamp']] = geladeira_log['status'].apply(lambda x: pd.Series(extract_voltage(x)))
device_log[['voltage', 'timestamp']] = device_log['status'].apply(lambda x: pd.Series(extract_voltage(x)))

# Concatenar as tabelas em um único DataFrame e remover valores nulos de voltagem
all_logs = pd.concat([cafeteira_log, geladeira_log, device_log])
all_logs_clean = all_logs.dropna(subset=['voltage', 'timestamp'])

# Normalizar os dados
scaler = StandardScaler()
X = scaler.fit_transform(all_logs_clean[['voltage']])

# Treinar o modelo de Isolation Forest
model = IsolationForest(contamination=0.01)  # Define a taxa de contaminação esperada
model.fit(X)

# Fazer previsões
all_logs_clean['anomaly'] = model.predict(X)

# As anomalias são marcadas como -1
anomalies = all_logs_clean[all_logs_clean['anomaly'] == -1]

# Agrupar por timestamp para verificar anomalias simultâneas
# Define a janela de tempo (em milissegundos) para considerar como "aproximado"
time_window = 60000  # 60 segundos

def find_simultaneous_anomalies(anomalies, time_window):
    anomalies_sorted = anomalies.sort_values(by='timestamp')
    simultaneous_anomalies = []

    for i, row in anomalies_sorted.iterrows():
        start_time = row['timestamp']
        end_time = start_time + time_window
        time_range_anomalies = anomalies_sorted[(anomalies_sorted['timestamp'] >= start_time) & (anomalies_sorted['timestamp'] <= end_time)]
        simultaneous_anomalies.append(time_range_anomalies)

    return pd.concat(simultaneous_anomalies).drop_duplicates()

simultaneous_anomalies = find_simultaneous_anomalies(anomalies, time_window)

# Visualização das anomalias simultâneas
for device_id in simultaneous_anomalies['device_id'].unique():
    device_logs = all_logs_clean[all_logs_clean['device_id'] == device_id]
    device_anomalies = simultaneous_anomalies[simultaneous_anomalies['device_id'] == device_id]

    if not device_anomalies.empty:
        plt.figure(figsize=(12, 6))
        plt.plot(device_logs['timestamp'], device_logs['voltage'], label="Voltagem", color='blue')
        plt.scatter(device_anomalies['timestamp'], device_anomalies['voltage'], color='red', label='Anomalias')
        plt.title(f'Análise de Anomalias Simultâneas para o Device ID: {device_id}')
        plt.xlabel('Timestamp')
        plt.ylabel('Voltagem (V)')
        plt.legend()
        plt.show()
