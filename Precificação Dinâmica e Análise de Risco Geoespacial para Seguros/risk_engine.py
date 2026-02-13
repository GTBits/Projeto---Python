import pandas as pd
import pickle
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from config import get_engine

def treinar_motor_risco():
    engine = get_engine()
    
    # Query SQL com JOIN (Trazendo tudo para uma visão analítica)
    query = """
    SELECT 
        p.Idade, p.Score_Credito, p.Latitude, p.Longitude,
        v.Valor_Fipe, v.Categoria_Risco,
        h.Teve_Sinistro
    FROM Policyholders p
    JOIN Vehicles v ON p.PolicyID = v.PolicyID
    JOIN Claims_History h ON p.PolicyID = h.PolicyID
    """
    
    print("🧠 Consolidando dados via SQL JOIN...")
    df = pd.read_sql(query, engine)
    
    X = df[['Idade', 'Score_Credito', 'Valor_Fipe', 'Categoria_Risco', 'Latitude', 'Longitude']]
    y = df['Teve_Sinistro']
    
    print("⚙️ Treinando Gradient Boosting (Risco de Sinistro)...")
    modelo = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
    modelo.fit(X, y)
    
    # Feature Importance (O que causa batidas?)
    importancias = pd.Series(modelo.feature_importances_, index=X.columns).sort_values(ascending=False)
    print("\n🔍 Fatores de Maior Risco:")
    print(importancias)
    
    with open('aigis_brain.pkl', 'wb') as f:
        pickle.dump(modelo, f)
    print("💾 Cérebro da AIGIS salvo.")

if __name__ == "__main__":
    treinar_motor_risco()