# 08_app.py
import streamlit as st
import pandas as pd
import time
from config import get_engine

# Configuração da Página
st.set_page_config(page_title="SENTINEL Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ SENTINEL - Monitor de Reputação em Tempo Real")
engine = get_engine()

# Função para carregar dados
def load_data():
    query = "SELECT * FROM Gold_Analytics ORDER BY ID_Analise DESC"
    return pd.read_sql(query, engine)

# Sidebar
st.sidebar.header("Painel de Controle")
if st.sidebar.button("Atualizar Dados"):
    st.rerun()

# KPIs Principais
df = load_data()
if not df.empty:
    col1, col2, col3 = st.columns(3)
    total_posts = len(df)
    
    # Contagem
    pos = len(df[df['Sentimento_Predito'] == 'Positivo'])
    neg = len(df[df['Sentimento_Predito'] == 'Negativo'])
    neu = len(df[df['Sentimento_Predito'] == 'Neutro'])
    
    col1.metric("Total de Menções", total_posts)
    col2.metric("Sentimento Positivo", f"{pos} 😀", delta_color="normal")
    col3.metric("Sentimento Negativo", f"{neg} 😡", delta_color="inverse")

    # Gráfico de Evolução
    st.subheader("Evolução do Sentimento (Últimos 100 posts)")
    chart_data = df.head(100)[['Sentimento_Predito', 'Data_Post']]
    st.scatter_chart(chart_data, x='Data_Post', y='Sentimento_Predito', color='Sentimento_Predito')

    # Tabela Recente
    st.subheader("Últimas Menções")
    st.dataframe(df[['Data_Post', 'Texto_Limpo', 'Sentimento_Predito', 'Probabilidade']].head(10))

else:
    st.warning("Aguardando dados...")

# Rodapé com Auto-Refresh
time.sleep(5)
st.rerun()