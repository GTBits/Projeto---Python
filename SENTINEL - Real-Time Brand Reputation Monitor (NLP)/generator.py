# 03_generator.py
import pandas as pd
import random
from faker import Faker
from datetime import datetime
import time
from config import get_engine # Importando do nosso arquivo 02

fake = Faker('pt_BR')
engine = get_engine()

comentarios_positivos = [
    "Amei o novo app do banco!", "Atendimento excelente", "Taxas muito baixas, recomendo",
    "Resolvi meu problema em 1 minuto", "O melhor banco digital", "Investimentos rendendo bem"
]
comentarios_negativos = [
    "O app não abre, que lixo", "Roubaram meu dinheiro", "Atendimento péssimo no chat",
    "Juros abusivos", "Vou cancelar minha conta", "Não consigo fazer pix", "Banco horrível"
]
comentarios_neutros = [
    "Como faço para mudar a senha?", "Qual o horário de funcionamento?", "Recebi um cartão novo",
    "Onde fica a agência?", "Atualização disponível"
]

def gerar_posts(n=10):
    lista = []
    print(f"🐦 Gerando {n} novos tweets...")
    for _ in range(n):
        tipo = random.choices(['Pos', 'Neg', 'Neu'], weights=[30, 20, 50])[0]
        
        if tipo == 'Pos': txt = random.choice(comentarios_positivos)
        elif tipo == 'Neg': txt = random.choice(comentarios_negativos)
        else: txt = random.choice(comentarios_neutros)
        
        # Adiciona ruído (emojis e erros) para dificultar pro NLP
        txt = f"{txt} {random.choice(['!!!', '...', '😡', '😍', ''])}"
        
        lista.append({
            'Usuario': fake.user_name(),
            'Texto_Original': txt,
            'Data_Post': datetime.now()
        })
    
    df = pd.DataFrame(lista)
    df.to_sql('Raw_Posts', engine, if_exists='append', index=False)
    print("✅ Ingestão concluída.")

if __name__ == "__main__":
    gerar_posts(20) # Gera 20 posts ao rodar