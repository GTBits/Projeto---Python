import pandas as pd
import sqlalchemy
import urllib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# --- 1. CONEXÃO COM O CHÃO DE FÁBRICA (SQL) ---
SERVER_NAME = '.' # <--- SEU SERVIDOR
DATABASE_NAME = 'VULTUR_DB'

params = urllib.parse.quote_plus(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;')
engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

print("🔌 Conectando ao VULTUR_DB...")

# --- 2. EXTRAÇÃO (Trazendo a Telemetria) ---
query = """
SELECT 
    Temperatura_C,
    Vibracao_mm_s,
    RPM,
    Pressao_Bar,
    Status_Rotulo
FROM Fato_Telemetria
"""
df = pd.read_sql(query, engine)
print(f"📊 Analisando {len(df)} leituras de sensores.")

# --- 3. PREPARAÇÃO (Traduzindo para a IA) ---
# A IA não lê texto. Vamos converter:
# Normal -> 0
# Alerta/Falha -> 1 (Isso é o que queremos prever!)
df['Target'] = df['Status_Rotulo'].apply(lambda x: 0 if x == 'Normal' else 1)

# Features (Os Sensores) vs Target (O Problema)
X = df[['Temperatura_C', 'Vibracao_mm_s', 'RPM', 'Pressao_Bar']]
y = df['Target']

# Separa 70% para treino e 30% para teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# --- 4. TREINAMENTO (A Mágica) ---
print("🤖 Treinando a Floresta Aleatória (Isso pode levar alguns segundos)...")
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# --- 5. RESULTADOS ---
previsoes = modelo.predict(X_test)

print("\n🎯 RELATÓRIO DE MANUTENÇÃO PREDITIVA:")
print(classification_report(y_test, previsoes, target_names=['Operação Normal', 'Risco de Falha']))

# --- 6. O GRÁFICO MAIS IMPORTANTE DA ENGENHARIA ---
# Feature Importance: Qual sensor avisa primeiro que vai dar ruim?
importancias = modelo.feature_importances_
sensores = X.columns

plt.figure(figsize=(10, 5))
sns.barplot(x=importancias, y=sensores, palette='viridis')
plt.title('Quais Sensores são os Melhores Preditores de Falha?')
plt.xlabel('Importância (0 a 1)')
plt.show()

# --- 7. EXPORTANDO O MODELO (BÔNUS) ---
# Em um projeto real, salvaríamos esse "cérebro" em um arquivo .pkl para usar no sistema
import pickle
with open('modelo_vultur_v1.pkl', 'wb') as file:
    pickle.dump(modelo, file)
print("💾 Modelo salvo como 'modelo_vultur_v1.pkl'. Pronto para deploy!")