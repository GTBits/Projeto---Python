# 04_cleaner.py
import re

def limpar_texto(texto):
    # 1. Tudo para minúsculo
    texto = str(texto).lower()
    # 2. Remove caracteres especiais (deixa só letras e espaços)
    texto = re.sub(r'[^\w\s]', '', texto)
    # 3. Remove números
    texto = re.sub(r'\d+', '', texto)
    return texto

# Teste rápido se rodar o arquivo direto
if __name__ == "__main__":
    print(limpar_texto("ODIEI!!! O app travou 3x hoje 😡 123"))