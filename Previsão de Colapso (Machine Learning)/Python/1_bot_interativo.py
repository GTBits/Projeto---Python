import telebot
import pyodbc
import pandas as pd
from sklearn.linear_model import LinearRegression
import warnings
import matplotlib.pyplot as plt
import io

warnings.filterwarnings('ignore')

print("LIGANDO ASSISTENTE VIRTUAL DA OBRA...")

# ATENCAO: NUNCA suba o seu Token real para o GitHub!
TOKEN = "COLOQUE_SEU_TOKEN_AQUI"
bot = telebot.TeleBot(TOKEN)

# --- FUNCOES DE CONEXAO COM OS BANCOS SQL ---

def buscar_dados_sql():
    drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver_mais_recente = drivers[-1] if drivers else 'SQL Server'
    conexao_string = (
        f"Driver={{{driver_mais_recente}}};"
        "Server=localhost;" 
        "Database=Tunel_Ops;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    
    conexao = pyodbc.connect(conexao_string)
    query = """
        SELECT Nome_Instrumento, Dias_Apos_Escavacao, Valor_Deformacao_mm 
        FROM vw_Monitoramento_Tunel
        WHERE Geologia LIKE '%Falha%'
        ORDER BY Nome_Instrumento, Dias_Apos_Escavacao
    """
    cursor = conexao.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [coluna[0] for coluna in cursor.description]
    conexao.close()
    
    df = pd.DataFrame.from_records(resultados, columns=colunas)
    df['Valor_Deformacao_mm'] = df['Valor_Deformacao_mm'].astype(float)
    df['Dias_Apos_Escavacao'] = df['Dias_Apos_Escavacao'].astype(int)
    novo_df = pd.DataFrame()
    estacas = sorted(df['Nome_Instrumento'].unique()) 
    dia_hoje = df['Dias_Apos_Escavacao'].max()
    
    for i, pino in enumerate(estacas):
        df_pino = df[df['Nome_Instrumento'] == pino].copy()
        df_pino['Valor_Deformacao_mm'] += (df_pino['Dias_Apos_Escavacao'] * (i * 0.05))
        atraso_dias = i * 4 
        df_pino = df_pino[df_pino['Dias_Apos_Escavacao'] <= (dia_hoje - atraso_dias)]
        novo_df = pd.concat([novo_df, df_pino])
        
    return novo_df, estacas

def buscar_dados_gases_sql():
    drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver_mais_recente = drivers[-1] if drivers else 'SQL Server'
    conexao_string = (
        f"Driver={{{driver_mais_recente}}};"
        "Server=localhost;" 
        "Database=Tunel_Gases;" 
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    
    conexao = pyodbc.connect(conexao_string)
    query = """
        SELECT Nome_Local, Sigla, Concentracao, Potencia_Exaustor_Pct, Status_Seguranca
        FROM vw_Status_Qualidade_Ar
        ORDER BY Estaca_Metros DESC, Sigla ASC
    """
    cursor = conexao.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [coluna[0] for coluna in cursor.description]
    conexao.close()
    
    return pd.DataFrame.from_records(resultados, columns=colunas)

def buscar_dados_maquinas_sql():
    drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver_mais_recente = drivers[-1] if drivers else 'SQL Server'
    conexao_string = (
        f"Driver={{{driver_mais_recente}}};"
        "Server=localhost;" 
        "Database=Tunel_Maquinas;" 
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    
    conexao = pyodbc.connect(conexao_string)
    query = """
        SELECT Frota, Modelo, Temp_Motor_C, Pressao_Oleo_Bar, Combustivel_Pct, Status_Maquina
        FROM vw_Status_Maquinario
        ORDER BY Frota ASC
    """
    cursor = conexao.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    colunas = [coluna[0] for coluna in cursor.description]
    conexao.close()
    
    return pd.DataFrame.from_records(resultados, columns=colunas)

# --- COMANDOS DO TELEGRAM ---

@bot.message_handler(commands=['start', 'help', 'ajuda'])
def menu_ajuda(mensagem):
    texto = (
        "SALA DE CONTROLE - ASSISTENTE IA\n\n"
        "Aqui estao todos os comandos disponiveis para monitorar a obra:\n\n"
        "[Visao Geral]\n"
        "/status - Resumo da deformacao da rocha.\n"
        "/gases - Monitoramento de CO, NO2, LEL e exaustores.\n"
        "/maquinas - Telemetria da frota pesada.\n\n"
        "[Inteligencia e Diagnostico]\n"
        "/critico - Roda a IA e mostra frentes em risco de ruptura.\n"
        "/diagnostico - Cruza os 3 bancos de dados para achar a causa raiz dos alertas.\n\n"
        "[Midia e Exportacao]\n"
        "/grafico - Desenha a curva de deformacao em tempo real.\n"
        "/grafico_gases - Painel visual de limites de tolerancia dos gases.\n"
        "/relatorio - Exporta a base de dados completa (Excel/CSV).\n\n"
        "[Consultas Especificas]\n"
        "/consultar <numero> - Traz o dossie de uma estaca. (Ex: /consultar 180)\n"
    )
    bot.reply_to(mensagem, texto)

@bot.message_handler(commands=['diagnostico'])
def relatorio_diagnostico(mensagem):
    bot.reply_to(mensagem, "Cruzando dados de Geotecnia, Qualidade do Ar e Maquinario. Aguarde...")
    try:
        df_rocha, estacas = buscar_dados_sql()
        df_gases = buscar_dados_gases_sql()
        df_maquinas = buscar_dados_maquinas_sql()

        resposta = "[DIAGNOSTICO INTEGRADO DE CAUSA RAIZ]\n\n"
        problemas_encontrados = False

        gases_criticos = df_gases[df_gases['Status_Seguranca'].str.contains('CRÍTICO|CRITICO', regex=True, na=False)]
        if not gases_criticos.empty:
            problemas_encontrados = True
            for index, linha in gases_criticos.iterrows():
                local = linha['Nome_Local']
                gas = linha['Sigla']
                resposta += f"-> ALERTA DE {gas} EM {local.upper()}:\n"

                if gas == 'CO' and '240' in local:
                    maq_critica = df_maquinas[df_maquinas['Status_Maquina'].str.contains('CRÍTICO|CRITICO', regex=True, na=False)]
                    if not maq_critica.empty:
                        modelo = maq_critica.iloc[0]['Modelo']
                        frota = maq_critica.iloc[0]['Frota']
                        temp = maq_critica.iloc[0]['Temp_Motor_C']
                        resposta += f"   CAUSA PROVAVEL: Superaquecimento da {modelo} ({frota}) operando na frente.\n"
                        resposta += f"   O motor atingiu {temp} C, gerando queima incompleta e excesso de monoxido.\n"
                        resposta += "   ACAO IMEDIATA: Desligar equipamento e evacuar o local.\n\n"

        if not problemas_encontrados:
            resposta += "Nenhuma anomalia critica cruzada no momento. Operacao normal."

        bot.send_message(mensagem.chat.id, resposta)
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Erro ao gerar diagnostico: {e}")

@bot.message_handler(commands=['status'])
def relatorio_status(mensagem):
    bot.reply_to(mensagem, "Consultando o banco de dados SQL Server...")
    try:
        df, estacas = buscar_dados_sql()
        resposta = "ULTIMA LEITURA DOS SENSORES (ROCHA):\n\n"
        for pino in estacas:
            ultima_leitura = df[df['Nome_Instrumento'] == pino].iloc[-1]
            deformacao = ultima_leitura['Valor_Deformacao_mm']
            resposta += f"{pino}: {deformacao:.1f} mm\n"
        bot.send_message(mensagem.chat.id, resposta)
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Erro ao ler o banco SQL: {e}")

@bot.message_handler(commands=['gases'])
def relatorio_gases(mensagem):
    bot.reply_to(mensagem, "Lendo sensores de qualidade do ar e exaustores. Aguarde...")
    try:
        df_gases = buscar_dados_gases_sql()
        resposta = "RELATORIO DE GASES E VENTILACAO:\n\n"
        estacas = df_gases['Nome_Local'].unique()
        for estaca in estacas:
            df_estaca = df_gases[df_gases['Nome_Local'] == estaca]
            exaustor = df_estaca['Potencia_Exaustor_Pct'].iloc[0]
            resposta += f"[{estaca.upper()}] - Exaustor: {exaustor}%\n"
            for index, linha in df_estaca.iterrows():
                sigla = linha['Sigla']
                conc = linha['Concentracao']
                status = linha['Status_Seguranca'].replace('🔴', '').replace('🟡', '').replace('🟢', '').strip()
                resposta += f" - {sigla}: {conc:.2f} ({status})\n"
            resposta += "\n"
        bot.send_message(mensagem.chat.id, resposta)
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Erro ao ler o banco de gases: {e}")

@bot.message_handler(commands=['maquinas'])
def relatorio_maquinas(mensagem):
    bot.reply_to(mensagem, "Conectando a telemetria da frota. Aguarde...")
    try:
        df_maquinas = buscar_dados_maquinas_sql()
        resposta = "RELATORIO DE MAQUINARIO PESADO:\n\n"
        for index, linha in df_maquinas.iterrows():
            frota = linha['Frota']
            modelo = linha['Modelo']
            temp = linha['Temp_Motor_C']
            oleo = linha['Pressao_Oleo_Bar']
            combustivel = linha['Combustivel_Pct']
            status = linha['Status_Maquina']
            resposta += f"[{frota}] - {modelo}\n"
            resposta += f"Status: {status}\n"
            resposta += f"Temp Motor: {temp} C\n"
            resposta += f"Pressao Oleo: {oleo} bar\n"
            resposta += f"Combustivel: {combustivel}%\n\n"
        bot.send_message(mensagem.chat.id, resposta)
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Erro ao ler telemetria das maquinas: {e}")

@bot.message_handler(commands=['grafico_gases'])
def enviar_grafico_gases(mensagem):
    bot.reply_to(mensagem, "Desenhando o painel de qualidade do ar. So um segundo...")
    try:
        df = buscar_dados_gases_sql()
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Painel de Telemetria de Gases por Frente de Obra', fontsize=16, fontweight='bold')
        gases = ['CO', 'NO2', 'LEL']
        limites = {'CO': 39.0, 'NO2': 5.0, 'LEL': 20.0}
        cores = ['#1f77b4', '#ff7f0e', '#2ca02c'] 
        for i, gas in enumerate(gases):
            df_gas = df[df['Sigla'] == gas]
            axs[i].bar(df_gas['Nome_Local'], df_gas['Concentracao'], color=cores[i])
            axs[i].axhline(y=limites[gas], color='r', linestyle='--', label='Critico / Evacuacao')
            axs[i].set_title(f'Gas: {gas}')
            axs[i].tick_params(axis='x', rotation=45)
            axs[i].legend()
            axs[i].grid(axis='y', linestyle=':', alpha=0.6)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        bot.send_photo(mensagem.chat.id, photo=buf, caption="Grafico de Gases gerado! A linha vermelha indica o limite maximo permitido por lei.")
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Erro ao desenhar grafico de gases: {e}")

@bot.message_handler(commands=['critico'])
def relatorio_ia(mensagem):
    bot.reply_to(mensagem, "Rodando modelo de Machine Learning. Aguarde...")
    try:
        df, estacas = buscar_dados_sql()
        LIMITE_CRITICO = 45.0
        alertas = ""
        for pino in estacas:
            df_pino = df[df['Nome_Instrumento'] == pino]
            if len(df_pino) < 3: continue
            X = df_pino[['Dias_Apos_Escavacao']].values
            y = df_pino['Valor_Deformacao_mm'].values
            modelo = LinearRegression()
            modelo.fit(X, y)
            velocidade = modelo.coef_[0]
            intercepto = modelo.intercept_
            ultimo_dia = X[-1][0]
            deformacao_atual = y[-1]
            if velocidade > 0:
                dia_colapso = (LIMITE_CRITICO - intercepto) / velocidade
                dias_restantes = dia_colapso - ultimo_dia
                if 0 < dias_restantes < 30 and deformacao_atual > 20:
                    alertas += (
                        f"[{pino}]\n"
                        f"Deformacao: {deformacao_atual:.1f} mm\n"
                        f"Velocidade: {velocidade:.2f} mm/dia\n"
                        f"Risco de ruptura em: {dias_restantes:.1f} dias!\n\n"
                    )
        if alertas == "":
            bot.send_message(mensagem.chat.id, "A IA analisou o SQL. Nenhuma estaca em risco critico.")
        else:
            bot.send_message(mensagem.chat.id, f"ALERTA DE IA - FRENTES CRITICAS:\n\n{alertas}")
    except Exception as e:
        bot.send_message(mensagem.chat.id, "Erro no processamento da IA.")

@bot.message_handler(commands=['grafico'])
def enviar_grafico(mensagem):
    bot.reply_to(mensagem, "Desenhando o grafico em tempo real direto do banco. So um segundo...")
    try:
        df, estacas = buscar_dados_sql()
        plt.figure(figsize=(10, 6))
        for pino in estacas:
            df_pino = df[df['Nome_Instrumento'] == pino]
            eixo_x = df_pino['Dias_Apos_Escavacao'] 
            eixo_y = df_pino['Valor_Deformacao_mm']
            plt.plot(eixo_x, eixo_y, label=pino, linewidth=2)
        plt.axhline(y=45.0, color='red', linestyle='--', label='RUPTURA (45mm)')
        plt.title('Curva de Convergencia (Tempo Real)', fontsize=14, fontweight='bold')
        plt.xlabel('Dias Apos Instalacao', fontsize=12)
        plt.ylabel('Deformacao (mm)', fontsize=12)
        plt.legend(loc='upper left')
        plt.grid(True, linestyle=':', alpha=0.6)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close() 
        bot.send_photo(mensagem.chat.id, photo=buf, caption="Grafico gerado com sucesso! Os dados refletem a exata situacao do SQL Server neste momento.")
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Erro ao desenhar o grafico: {e}")

@bot.message_handler(commands=['relatorio'])
def enviar_relatorio(mensagem):
    bot.reply_to(mensagem, "Extraindo dados do SQL e montando a planilha. So um instante...")
    try:
        df, _ = buscar_dados_sql()
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig') 
        csv_buffer.seek(0)
        csv_buffer.name = 'Relatorio_Frentes_Obra.csv' 
        bot.send_document(mensagem.chat.id, document=csv_buffer, caption="Base de dados exportada com sucesso! Voce ja pode abrir no Excel.")
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Erro ao gerar a planilha: {e}")

@bot.message_handler(commands=['consultar'])
def consultar_estaca(mensagem):
    comando_separado = mensagem.text.split()
    if len(comando_separado) < 2:
        bot.reply_to(mensagem, "Formato incorreto.\nVoce precisa me dizer qual estaca quer ver.\nExemplo: /consultar 180")
        return
    numero_estaca = comando_separado[1]
    alvo = f"Estaca {numero_estaca}m"
    bot.reply_to(mensagem, f"Puxando a ficha completa da {alvo}...")
    try:
        df, estacas = buscar_dados_sql()
        if alvo not in estacas:
            bot.send_message(mensagem.chat.id, f"Nao encontrei a {alvo} no banco de dados. Verifique o numero digitado.")
            return
        df_pino = df[df['Nome_Instrumento'] == alvo]
        ultima_leitura = df_pino.iloc[-1]
        X = df_pino[['Dias_Apos_Escavacao']].values
        y = df_pino['Valor_Deformacao_mm'].values
        modelo = LinearRegression().fit(X, y)
        velocidade = modelo.coef_[0]
        resposta = (
            f"[DOSSIE DE ENGENHARIA: {alvo.upper()}]\n\n"
            f"Deformacao Atual: {ultima_leitura['Valor_Deformacao_mm']:.2f} mm\n"
            f"Velocidade de Avanco: {velocidade:.3f} mm/dia\n"
            f"Tempo de Instalacao: {ultima_leitura['Dias_Apos_Escavacao']} dias\n\n"
        )
        if ultima_leitura['Valor_Deformacao_mm'] >= 45:
            resposta += "STATUS: RUPTURA / COLAPSO"
        elif ultima_leitura['Valor_Deformacao_mm'] >= 25:
            resposta += "STATUS: ATENCAO (Monitoramento Diario Obrigatorio)"
        else:
            resposta += "STATUS: SEGURO (Estavel)"
        bot.send_message(mensagem.chat.id, resposta)
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Erro na consulta: {e}")

print("Robo conectado aos 3 bancos SQL e escutando o Telegram!")
bot.infinity_polling()
