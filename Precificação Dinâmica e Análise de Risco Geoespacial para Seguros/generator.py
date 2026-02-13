import pandas as pd
import numpy as np
from faker import Faker
import random
from config import get_engine
from sqlalchemy import text # Importante para rodar SQL puro

fake = Faker('pt_BR')
engine = get_engine()

def limpar_banco_seguro():
    """Limpa as tabelas na ordem correta para não quebrar FK"""
    print("🧹 Limpando dados antigos...")
    with engine.connect() as conn:
        # Ordem: Primeiro deleta os Filhos, depois o Pai
        conn.execute(text("DELETE FROM Claims_History"))
        conn.execute(text("DELETE FROM Vehicles"))
        conn.execute(text("DELETE FROM Policyholders"))
        conn.commit()
    print("✨ Banco limpo.")

def gerar_carteira_seguros(n=5000):
    # 1. Limpa a casa antes de começar
    limpar_banco_seguro()
    
    print(f"🛡️ Gerando {n} apólices com dados geoespaciais...")
    
    clientes = []
    veiculos = []
    historico = []
    
    # Coordenadas base (São Paulo)
    lat_base = -23.5505
    lon_base = -46.6333
    
    for i in range(1, n+1):
        # ... (A LÓGICA PERMANECE A MESMA DA VERSÃO ANTERIOR) ...
        # Vou resumir aqui para focar na correção, mantenha sua lógica de geração!
        
        idade = random.randint(18, 75)
        score = random.randint(300, 850)
        genero = random.choice(['M', 'F'])
        lat = lat_base + random.uniform(-0.1, 0.1)
        lon = lon_base + random.uniform(-0.1, 0.1)
        zona_risco = 1 if (lat < -23.6 and lon > -46.6) else 0 
        
        clientes.append({
            'PolicyID': i, 'Nome': fake.name(), 'Idade': idade, 
            'Genero': genero, 'Estado_Civil': random.choice(['Solteiro', 'Casado']),
            'Score_Credito': score, 'Latitude': lat, 'Longitude': lon
        })
        
        tipo = random.choice(['Sedan', 'SUV', 'Hatch', 'Esportivo'])
        valor = random.uniform(30000, 150000)
        cat_risco = 5 if tipo == 'Esportivo' else random.randint(1, 3)
        if zona_risco: cat_risco += 1
        
        veiculos.append({
            'VehicleID': i, 'PolicyID': i, 'Modelo': f"{tipo} {fake.color_name()}",
            'Ano_Modelo': random.randint(2015, 2025), 'Valor_Fipe': round(valor, 2),
            'Categoria_Risco': min(cat_risco, 5)
        })
        
        prob_sinistro = 0.05
        if idade < 25: prob_sinistro += 0.10
        if tipo == 'Esportivo': prob_sinistro += 0.08
        if zona_risco: prob_sinistro += 0.15
        
        teve_sinistro = 1 if random.random() < prob_sinistro else 0
        custo = valor * random.uniform(0.1, 1.0) if teve_sinistro else 0
        premio_justo = (valor * 0.03) + (custo * 0.5)
        
        historico.append({
            'HistoryID': i, 'PolicyID': i, 'Teve_Sinistro': teve_sinistro,
            'Custo_Sinistro': round(custo, 2), 'Premio_Anual_Pago': round(premio_justo, 2)
        })

    # --- AQUI ESTÁ A CORREÇÃO NO SALVAMENTO ---
    # Usamos 'append' para respeitar a estrutura criada no SQL
    # E salvamos na ordem: Pai primeiro, Filhos depois
    
    print("💾 Salvando Clientes (Pai)...")
    pd.DataFrame(clientes).to_sql('Policyholders', engine, if_exists='append', index=False)
    
    print("💾 Salvando Veículos e Histórico (Filhos)...")
    pd.DataFrame(veiculos).to_sql('Vehicles', engine, if_exists='append', index=False)
    pd.DataFrame(historico).to_sql('Claims_History', engine, if_exists='append', index=False)
    
    print("✅ Dados complexos gerados com sucesso.")

if __name__ == "__main__":
    gerar_carteira_seguros()