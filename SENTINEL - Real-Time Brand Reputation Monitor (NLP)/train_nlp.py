# 05_train_nlp.py
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import pickle
from cleaner import limpar_texto # Importando nosso arquivo 04

# DADOS DE TREINO (Hardcoded para ensinar o básico pro robô)
data = {
    'texto': [
        'amei muito bom', 'excelente serviço', 'adoro esse banco', 'maravilhoso', 'lucro alto',
        'péssimo horrivel', 'odeio', 'lixo de app', 'trava muito', 'ladrões', 'juros altos',
        'ok', 'normal', 'tanto faz', 'recebi', 'dúvida'
    ],
    'sentimento': [
        'Positivo', 'Positivo', 'Positivo', 'Positivo', 'Positivo',
        'Negativo', 'Negativo', 'Negativo', 'Negativo', 'Negativo', 'Negativo',
        'Neutro', 'Neutro', 'Neutro', 'Neutro', 'Neutro'
    ]
}

print("🧠 Treinando IA de Análise de Sentimento...")
df_treino = pd.DataFrame(data)
df_treino['texto_limpo'] = df_treino['texto'].apply(limpar_texto)

# Pipeline: Transforma Texto em Números -> Aplica Regressão Logística
modelo = make_pipeline(CountVectorizer(), LogisticRegression())
modelo.fit(df_treino['texto_limpo'], df_treino['sentimento'])

# Salva o cérebro
with open('modelo_sentinel.pkl', 'wb') as f:
    pickle.dump(modelo, f)

print("💾 Modelo salvo como 'modelo_sentinel.pkl'")