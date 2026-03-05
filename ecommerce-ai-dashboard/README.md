# 📊 E-Commerce AI & Executive Analytics Dashboard

Este projeto é uma solução completa de Business Intelligence (BI) e Machine Learning aplicada ao varejo. Ele extrai dados de um banco relacional (Star Schema), analisa métricas de negócio e utiliza Inteligência Artificial para prever o faturamento futuro.

## 🚀 Funcionalidades
* **Predição Sazonal com IA:** Utiliza o algoritmo `RandomForestRegressor` para analisar o histórico de vendas e prever os próximos 12 meses, respeitando picos sazonais (ex: Black Friday, Natal).
* **Cross-Filtering Interativo:** Gráficos totalmente conectados (estilo Power BI). Clicar em um canal de marketing recalcula toda a previsão e as métricas na hora.
* **KPIs Executivos:** Acompanhamento de Faturamento Total, Ticket Médio, Custo de Logística (Frete) e Nota de Qualidade do Cliente.
* **Geolocalização:** Mapeamento dos Top Estados com maior volume de faturamento.

## 🛠️ Tecnologias Utilizadas
* **Banco de Dados:** Microsoft SQL Server (Modelagem Star Schema)
* **Engenharia e Análise de Dados:** Python (Pandas, Numpy)
* **Machine Learning:** Scikit-Learn
* **Front-end / Dashboard:** Dash by Plotly

## ⚙️ Como executar o projeto localmente

1. Clone este repositório:
```bash
git clone [https://github.com/SEU-USUARIO/ecommerce-ai-dashboard.git](https://github.com/SEU-USUARIO/ecommerce-ai-dashboard.git)
pip install -r requirements.txt
python app.py
