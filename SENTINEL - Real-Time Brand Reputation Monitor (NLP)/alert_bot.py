# 07_alert_bot.py
import pandas as pd
from config import get_engine, LIMITE_CRISE

def checar_crise():
    engine = get_engine()
    
    # Pega os últimos 50 posts
    query = "SELECT TOP 50 Sentimento_Predito FROM Gold_Analytics ORDER BY ID_Analise DESC"
    df = pd.read_sql(query, engine)
    
    if len(df) < 10: return # Poucos dados ainda

    total = len(df)
    negativos = len(df[df['Sentimento_Predito'] == 'Negativo'])
    taxa_negativa = negativos / total

    print(f"📊 Taxa de Negatividade Atual: {taxa_negativa:.1%}")

    if taxa_negativa > LIMITE_CRISE:
        print("🚨 ALERTA VERMELHO: Crise de Reputação Detectada! Enviando e-mail para CEO...")
        # Aqui entraria um código de envio de e-mail (SMTP)
    else:
        print("🟢 Reputação Estável.")

if __name__ == "__main__":
    checar_crise()