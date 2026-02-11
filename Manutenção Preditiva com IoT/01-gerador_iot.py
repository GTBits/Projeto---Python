import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO ---
SERVER_NAME = '.' # <--- SEU SERVIDOR
DATABASE_NAME = 'VULTUR_DB'

# Conexão SQL
params = urllib.parse.quote_plus(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;')
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

print("🏭 Iniciando simulação de Sensores Industriais (IoT)...")

def gerar_dados_maquina(id_maquina, dias=365):
    """
    Simula um motor que opera normal, mas às vezes degrada até falhar.
    """
    data_inicial = datetime.now() - timedelta(days=dias)
    freq = '1h' # Dados de hora em hora
    datas = pd.date_range(start=data_inicial, end=datetime.now(), freq=freq)
    n = len(datas)
    
    # 1. BASELINE (Comportamento Normal)
    # Temperatura média 65°C, Vibração 2mm/s, RPM 1800
    temp = np.random.normal(65, 2, n) 
    vibracao = np.random.normal(2, 0.5, n)
    rpm = np.random.normal(1800, 20, n)
    pressao = np.random.normal(120, 5, n) # Bar
    
    # 2. INJETANDO FALHAS (DEGRADAÇÃO)
    # Vamos simular 3 falhas durante o ano
    falhas = []
    status = ['Normal'] * n
    
    # Escolhemos 3 momentos aleatórios para começar a quebrar
    pontos_de_falha = np.sort(np.random.choice(range(100, n-100), 3, replace=False))
    
    for ponto in pontos_de_falha:
        duracao_problema = np.random.randint(24, 100) # O problema dura entre 1 a 4 dias
        fim = min(ponto + duracao_problema, n)
        
        # Durante esse tempo, os sensores "enlouquecem" (Drift)
        # Temperatura sobe linearmente até +40 graus
        temp[ponto:fim] += np.linspace(0, 40, fim-ponto)
        # Vibração aumenta exponencialmente
        vibracao[ponto:fim] += np.linspace(0, 8, fim-ponto)
        # Pressão cai
        pressao[ponto:fim] -= np.linspace(0, 30, fim-ponto)
        
        # Marcamos os últimos registros como "FALHA IMINENTE"
        for i in range(ponto, fim):
            status[i] = 'Alerta'
        
        # O último ponto é a quebra
        status[fim-1] = 'Falha Critica'
        falhas.append(datas[fim-1])

    # Cria o DataFrame
    df = pd.DataFrame({
        'Data_Leitura': datas,
        'ID_Maquina': f'Motor-{id_maquina:02d}',
        'Temperatura_C': temp,
        'Vibracao_mm_s': vibracao,
        'RPM': rpm,
        'Pressao_Bar': pressao,
        'Status_Rotulo': status # O alvo do nosso Machine Learning
    })
    
    return df

# --- LOOP PARA GERAR MÚTIPLAS MÁQUINAS ---
lista_dfs = []
for i in range(1, 6): # 5 Máquinas
    print(f"⚙️ Simulando Motor-0{i}...")
    df_maq = gerar_dados_maquina(i)
    lista_dfs.append(df_maq)

df_final = pd.concat(lista_dfs)

print(f"💾 Salvando {len(df_final)} leituras de telemetria no SQL Server...")
df_final.to_sql('Fato_Telemetria', con=engine, if_exists='replace', index=False)

print("✅ SUCESSO! O VULTUR_DB está vivo.")