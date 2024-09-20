import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import random

# Defina o caminho da pasta que contém os arquivos .xlsx
caminho_pasta = '/Users/novaki/Downloads'

# Nome do arquivo principal que armazenará todos os dados filtrados
arquivo_completo = 'dados_filtrados.xlsx'

# Carrega os dados existentes do arquivo completo, se ele já existir
if os.path.exists(arquivo_completo):
    dados_filtrados = pd.read_excel(arquivo_completo)
else:
    dados_filtrados = pd.DataFrame()

# Lista para armazenar os novos dados filtrados desta execução
novos_dados_filtrados = []

# Total de registros em todos os arquivos na pasta
total_base = 0

# Percorre todos os arquivos na pasta
for arquivo in os.listdir(caminho_pasta):
    # Verifica se o arquivo tem a extensão .xlsx
    if arquivo.endswith('.xlsx'):
        # Lê o arquivo Excel
        caminho_arquivo = os.path.join(caminho_pasta, arquivo)
        df = pd.read_excel(caminho_arquivo)

        # Soma o total de registros em todos os arquivos da pasta
        total_base += len(df)

        # Verifica se a coluna 'Mobile' existe no DataFrame
        if 'Mobile' in df.columns:
            # Filtra os registros onde a coluna 'Mobile' não está vazia
            df_filtrado = df[df['Mobile'].notna()]

            # Adiciona os novos dados filtrados à lista
            novos_dados_filtrados.append(df_filtrado)
        else:
            print(f"A coluna 'Mobile' não foi encontrada no arquivo: {arquivo}")

# Combina todos os novos dados filtrados em um único DataFrame
if novos_dados_filtrados:
    novos_dados = pd.concat(novos_dados_filtrados, ignore_index=True)

    # Remove duplicatas com base na coluna 'Mobile', comparando com os dados antigos
    if 'Mobile' in dados_filtrados.columns:
        novos_dados_unicos = novos_dados[~novos_dados['Mobile'].isin(dados_filtrados['Mobile'])]
    else:
        novos_dados_unicos = novos_dados

    # Atualiza o arquivo completo com os novos dados únicos (sem duplicatas)
    dados_filtrados_atualizado = pd.concat([dados_filtrados, novos_dados_unicos], ignore_index=True)

    # Salva o arquivo completo com todos os dados desde o início
    dados_filtrados_atualizado.to_excel(arquivo_completo, index=False)

    # Salva um novo arquivo apenas com os novos dados únicos desta execução
    data_atual = datetime.now().strftime('%Y-%m-%d')
    arquivo_novos_dados = f'dados_filtrados_{data_atual}.xlsx'

    # Verifica se há novos dados antes de salvar
    if not novos_dados_unicos.empty:
        novos_dados_unicos.to_excel(arquivo_novos_dados, index=False)
        print(f"Arquivo '{arquivo_novos_dados}' criado com os novos registros desta execução.")
    else:
        print("Nenhum novo dado foi encontrado. Nenhum arquivo de novos registros foi criado.")

    print(f"'dados_filtrados.xlsx' foi atualizado com todos os dados desde o início.")
else:
    print("Nenhum dado válido foi encontrado nos arquivos .xlsx.")

# Total com telefone (total em dados_filtrados.xlsx)
total_com_telefone = len(dados_filtrados_atualizado[dados_filtrados_atualizado['Mobile'].notna()])

# Criar gráfico de evolução
historico_datas = []
historico_quantidades = []

# Percorre os arquivos 'dados_filtrados_YYYY-MM-DD.xlsx' para extrair a quantidade de novos registros diários
for arquivo in os.listdir():
    if arquivo.startswith('dados_filtrados_') and arquivo.endswith('.xlsx'):
        data_str = arquivo.replace('dados_filtrados_', '').replace('.xlsx', '')
        df_diario = pd.read_excel(arquivo)
        qtd_diario = len(df_diario[df_diario['Mobile'].notna()])
        historico_datas.append(data_str)
        historico_quantidades.append(qtd_diario)

# Criar gráfico da evolução dos registros diários (barras finas com cor azul fixa)
plt.figure(figsize=(10, 6))

# Cor fixa azul para as barras
cor_barra = '#1f77b4'  # Cor azul

# Gráfico de barras finas com espaçamento adequado
largura_barra = 0.4  # Reduzindo a largura das barras
bar_positions = range(len(historico_datas))  # Posições das barras
espacamento_barra = 0.2  # Adicionando espaçamento entre as barras

plt.bar([p + espacamento_barra for p in bar_positions], historico_quantidades, width=largura_barra, color=cor_barra, label='Quantidade por dia')

# Adicionar a linha de evolução (vermelha)
plt.plot(bar_positions, historico_quantidades, marker='o', color='red', linestyle='-', label='Evolução (linha)')

# Adicionar os valores em cada pico
for i, valor in enumerate(historico_quantidades):
    plt.text(i, valor + 0.5, str(valor), ha='center', va='bottom')

# Ajustar eixos e layout
plt.title('Evolução Diária de Registros com Telefone')
plt.xlabel('Data')
plt.ylabel('Quantidade de Registros')
plt.xticks(bar_positions, historico_datas, rotation=45)
plt.legend()

# Ajuste de layout
plt.tight_layout()

# Salvar gráfico como imagem
grafico_path = 'grafico_evolucao.png'
plt.savefig(grafico_path)
plt.close()

# Gerar PDF com as informações
pdf = FPDF()
pdf.add_page()

# Título
pdf.set_font('Arial', 'B', 16)
pdf.cell(200, 10, 'Relatório de Registros com Telefone', ln=True, align='C')

# Texto de total da base
pdf.set_font('Arial', '', 12)
pdf.ln(10)
pdf.cell(200, 10, f'Total de registros na base (todos os usúarios): {total_base}', ln=True)
pdf.cell(200, 10, f'Total de registros com telefone: {total_com_telefone}', ln=True)

# Adicionar gráfico ao PDF
pdf.ln(10)
pdf.image(grafico_path, x=10, y=pdf.get_y(), w=pdf.w - 20)

# Salvar o PDF
arquivo_pdf = f'relatorio_{data_atual}.pdf'
pdf.output(arquivo_pdf)

print(f"Relatório PDF '{arquivo_pdf}' criado com sucesso.")
