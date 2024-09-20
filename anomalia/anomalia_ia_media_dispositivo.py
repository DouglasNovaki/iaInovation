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
        return voltages[0] if voltages else None
    except (ValueError, SyntaxError):
        return None

# Aplicar a função para extrair a voltagem em cada log
cafeteira_log['voltage'] = cafeteira_log['status'].apply(extract_voltage)
geladeira_log['voltage'] = geladeira_log['status'].apply(extract_voltage)
device_log['voltage'] = device_log['status'].apply(extract_voltage)

# Concatenar as tabelas em um único DataFrame e remover valores nulos de voltagem
all_logs = pd.concat([cafeteira_log, geladeira_log, device_log])
all_logs_clean = all_logs.dropna(subset=['voltage'])

# Função para detectar anomalias com base nos limites ajustados para cada dispositivo
def detect_anomalies_by_device(logs, device_id):
    device_logs = logs[logs['device_id'] == device_id].copy()

    if len(device_logs) < 10:
        print(f"Dispositivo {device_id} ignorado (menos de 10 logs).")
        return pd.DataFrame(), pd.DataFrame()

    # Calcular a média da voltagem e os limites de anomalia para o dispositivo
    mean_voltage = device_logs['voltage'].mean()
    lower_limit = mean_voltage * 0.90
    upper_limit = mean_voltage * 1.10

    # Normalizar os dados para detecção de anomalias
    scaler = StandardScaler()
    scaled_voltages = scaler.fit_transform(device_logs[['voltage']])

    # Treinar o modelo de detecção de anomalias
    model = IsolationForest(contamination=0.05, random_state=42)
    device_logs['anomaly'] = model.fit_predict(scaled_voltages)

    # Identificar anomalias
    anomalies = device_logs[device_logs['anomaly'] == -1]

    # Filtrar anomalias baseadas na variação da média
    anomalies_filtered = anomalies[(anomalies['voltage'] < lower_limit) | (anomalies['voltage'] > upper_limit)]

    # Adicionar colunas de limites para visualização
    device_logs['lower_limit'] = lower_limit
    device_logs['upper_limit'] = upper_limit

    return device_logs, anomalies_filtered

# Obter os device_ids únicos e detectar anomalias para cada um
device_ids = all_logs_clean['device_id'].unique()

for device_id in device_ids:
    device_logs, anomalies = detect_anomalies_by_device(all_logs_clean, device_id)

    if not anomalies.empty:
        plt.figure(figsize=(10, 6))
        plt.plot(device_logs.index, device_logs['voltage'], label="Voltagem", color='blue')
        plt.axhline(y=device_logs['lower_limit'].iloc[0], color='red', linestyle='--', label=f'Limite Inferior ({device_logs["lower_limit"].iloc[0]:.1f}V)')
        plt.axhline(y=device_logs['upper_limit'].iloc[0], color='red', linestyle='--', label=f'Limite Superior ({device_logs["upper_limit"].iloc[0]:.1f}V)')
        plt.scatter(anomalies.index, anomalies['voltage'], color='orange', label='Anomalias')
        plt.title(f'Análise de Anomalias para o Device ID: {device_id}')
        plt.xlabel('Índice do Log')
        plt.ylabel('Voltagem (V)')
        plt.legend()
        plt.show()
