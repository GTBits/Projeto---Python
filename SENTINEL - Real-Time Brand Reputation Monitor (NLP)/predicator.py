import pandas as pd
import pickle
from config import get_engine
from cleaner import limpar_texto
from sqlalchemy import text  # <--- Importação necessária para o UPDATE funcionar

def processar_novos_posts():
    engine = get_engine()
    
    # 1. Carrega o Modelo
    try:
        with open('modelo_sentinel.pkl', 'rb') as f:
            modelo = pickle.load(f)
    except FileNotFoundError:
        print("❌ ERRO: O arquivo 'modelo_sentinel.pkl' não existe. Rode o '05_train_nlp.py' primeiro!")
        return
    
    # 2. Busca posts que ainda não foram processados (Processado = 0)
    # Usamos text() aqui também para garantir compatibilidade total
    query = text("SELECT * FROM Raw_Posts WHERE Processado = 0")
    df_novos = pd.read_sql(query, engine)
    
    if len(df_novos) == 0:
        print("💤 Nenhum post novo para analisar.")
        return

    print(f"⚡ Analisando {len(df_novos)} posts...")

    # 3. Limpa e Prevê
    # Garante que o texto seja string antes de limpar
    df_novos['Texto_Limpo'] = df_novos['Texto_Original'].astype(str).apply(limpar_texto)
    
    # Faz a predição
    df_novos['Sentimento_Predito'] = modelo.predict(df_novos['Texto_Limpo'])
    
    # Pega a probabilidade (certeza)
    probs = modelo.predict_proba(df_novos['Texto_Limpo'])
    df_novos['Probabilidade'] = [max(p) for p in probs]

    # 4. Salva na Gold Analytics
    df_gold = df_novos[['ID_Post', 'Data_Post', 'Texto_Limpo', 'Sentimento_Predito', 'Probabilidade']]
    df_gold.to_sql('Gold_Analytics', engine, if_exists='append', index=False)

    # 5. Marca como processado na Raw (UPDATE no SQL)
    ids_processados = tuple(df_novos['ID_Post'].tolist())
    
    # Tratamento para tupla: SQL não aceita "(1,)" com vírgula no final, precisa ser "(1)"
    str_ids = str(ids_processados)
    if len(ids_processados) == 1:
        str_ids = f"({ids_processados[0]})"
    
    # Executa o UPDATE seguro
    with engine.connect() as conn:
        sql_update = text(f"UPDATE Raw_Posts SET Processado = 1 WHERE ID_Post IN {str_ids}")
        conn.execute(sql_update)
        conn.commit()
        
    print("✅ Análise concluída e salva na Gold.")

if __name__ == "__main__":
    processar_novos_posts()