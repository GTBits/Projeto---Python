import streamlit as st
import pandas as pd
import pickle
import numpy as np
from sqlalchemy import text
from config import get_engine

st.set_page_config(page_title="AIGIS - Underwriting AI", layout="wide", page_icon="🛡️")

# CSS Customizado
st.markdown("""
<style>
    .stMetric {background-color: #0E1117; border: 1px solid #333; padding: 15px; border-radius: 5px;}
    h1, h2, h3 {color: #4F8BF9;}
</style>
""", unsafe_allow_html=True)

# --- OTIMIZAÇÃO 1: Cache na Conexão (Só conecta uma vez) ---
@st.cache_resource
def get_db_connection():
    return get_engine()

# --- OTIMIZAÇÃO 2: Cache nos Dados (Não faz SELECT toda hora) ---
@st.cache_data
def load_data():
    engine = get_db_connection()
    query = """
    SELECT p.Latitude, p.Longitude, h.Teve_Sinistro, h.Custo_Sinistro, h.Premio_Anual_Pago
    FROM Policyholders p
    JOIN Claims_History h ON p.PolicyID = h.PolicyID
    """
    return pd.read_sql(query, engine)

def main():
    st.title("🛡️ AIGIS - Intelligent Underwriting System")
    
    # Debug para saber se travou
    st.write("🔄 Carregando dados...")
    
    # Usa a função com cache
    df = load_data()
    
    # Remove mensagem de carregando se passou daqui
    st.empty() 
    
    try:
        with open('aigis_brain.pkl', 'rb') as f:
            modelo = pickle.load(f)
    except:
        st.error("Modelo não encontrado. Rode o script 02 primeiro.")
        return

    # --- SIDEBAR: SIMULADOR DE COTAÇÃO ---
    st.sidebar.header("🚘 Novo Cliente (Simulação)")
    
    s_idade = st.sidebar.slider("Idade", 18, 80, 30)
    s_fipe = st.sidebar.number_input("Valor do Carro (FIPE)", 20000, 300000, 50000)
    s_score = st.sidebar.slider("Score Serasa", 0, 1000, 600)
    s_cat = st.sidebar.selectbox("Categoria Risco Veículo", [1, 2, 3, 4, 5], index=2)
    s_lat = st.sidebar.number_input("Lat", value=-23.55, format="%.4f")
    s_lon = st.sidebar.number_input("Lon", value=-46.63, format="%.4f")

    if st.sidebar.button("CALCULAR PRÊMIO"):
        entrada = pd.DataFrame([[s_idade, s_score, s_fipe, s_cat, s_lat, s_lon]], 
                               columns=['Idade', 'Score_Credito', 'Valor_Fipe', 'Categoria_Risco', 'Latitude', 'Longitude'])
        
        prob_sinistro = modelo.predict_proba(entrada)[0][1]
        custo_esperado = prob_sinistro * (s_fipe * 0.40)
        margem = 1.30 
        preco_final = custo_esperado * margem
        if preco_final < 1000: preco_final = 1000 
        
        st.sidebar.success(f"💰 Prêmio Sugerido: R$ {preco_final:,.2f}")
        st.sidebar.info(f"⚠️ Probabilidade de Sinistro: {prob_sinistro:.1%}")
        
        if prob_sinistro > 0.30:
            st.sidebar.error("CLIENTE DE ALTO RISCO")
        elif prob_sinistro < 0.10:
            st.sidebar.success("CLIENTE VIP (BAIXO RISCO)")
        else:
            st.sidebar.warning("RISCO MODERADO")

    # --- DASHBOARD PRINCIPAL ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    loss_ratio = (df['Custo_Sinistro'].sum() / df['Premio_Anual_Pago'].sum()) * 100
    
    kpi1.metric("Carteira Total", len(df))
    kpi2.metric("Sinistralidade (Loss Ratio)", f"{loss_ratio:.1f}%", "-Ideal < 60%")
    kpi3.metric("Sinistros Totais", df['Teve_Sinistro'].sum())
    
    # Tratamento para evitar divisão por zero se ninguém bateu
    custo_medio = 0
    df_sinistrados = df[df['Custo_Sinistro']>0]
    if not df_sinistrados.empty:
        custo_medio = df_sinistrados['Custo_Sinistro'].mean()
        
    kpi4.metric("Custo Médio Sinistro", f"R$ {custo_medio:,.2f}")

    st.markdown("---")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("🗺️ Mapa de Calor de Sinistros")
        st.caption("Pontos vermelhos indicam locais de residência de clientes que tiveram sinistro.")
        
        df_batidas = df[df['Teve_Sinistro'] == 1][['Latitude', 'Longitude']]
        
        # Renomeando para o mapa funcionar
        df_batidas = df_batidas.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
        
        if not df_batidas.empty:
            st.map(df_batidas, size=20, color='#FF0000') 
        else:
            st.warning("Sem dados de sinistro para o mapa.")

    with c2:
        st.subheader("📊 Fatores de Risco")
        st.write("Maiores Sinistros Pagos")
        st.dataframe(df_sinistrados['Custo_Sinistro'].sort_values(ascending=False).head(10))

if __name__ == "__main__":
    main()