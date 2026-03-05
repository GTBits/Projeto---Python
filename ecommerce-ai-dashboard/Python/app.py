import dash
from dash import dcc, html, Input, Output, ctx
import pandas as pd
import plotly.graph_objects as go
import pyodbc
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# --- 1. CONEXÃO E EXTRAÇÃO DE DADOS (STAR SCHEMA AVANÇADO) ---
def buscar_dados():
    drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver_f = drivers[-1] if drivers else 'SQL Server'
    conn_str = f"Driver={{{driver_f}}};Server=.;Database=Ecommerce_DB;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    
    query = """
        SELECT 
            v.Data_Venda, c.Nome_Categoria, vend.Nome_Vendedor, p.Nome_Produto,
            v.Quantidade, (v.Quantidade * p.Preco_Venda) as Faturamento,
            v.UF_Destino, v.Valor_Frete, v.Nota_Avaliacao,
            t.Nome_Transportadora, m.Nome_Canal
        FROM Vendas v
        JOIN Produtos p ON v.ID_Produto = p.ID_Produto
        JOIN Categorias c ON p.ID_Categoria = c.ID_Categoria
        JOIN Vendedores vend ON v.ID_Vendedor = vend.ID_Vendedor
        JOIN Transportadoras t ON v.ID_Transportadora = t.ID_Transportadora
        JOIN Canais_Marketing m ON v.ID_Canal = m.ID_Canal
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df_master = buscar_dados()
df_master['Data_Venda'] = pd.to_datetime(df_master['Data_Venda'])

data_min = df_master['Data_Venda'].min()
data_max = df_master['Data_Venda'].max()

# --- 2. INTERFACE E ESTILOS ---
app = dash.Dash(__name__)

kpi_style = {
    'backgroundColor': '#1a1a1a', 'padding': '15px', 'borderRadius': '10px', 
    'width': '23%', 'textAlign': 'center', 'boxShadow': '0px 4px 10px rgba(0,212,255,0.1)',
    'borderTop': '3px solid #00d4ff'
}

app.layout = html.Div(style={'backgroundColor': '#0a0a0a', 'color': 'white', 'padding': '20px', 'fontFamily': 'Segoe UI'}, children=[
    html.H1("🚀 Ultimate Analytics & IA Sazonal", style={'textAlign': 'center', 'color': '#00d4ff', 'marginBottom': '30px'}),
    
    html.Div([
        html.Div([
            html.Label("Categorias (Multi):", style={'display': 'block'}),
            dcc.Dropdown(id='filtro-categoria', 
                         options=[{'label': c, 'value': c} for c in sorted(df_master['Nome_Categoria'].unique())],
                         value=list(df_master['Nome_Categoria'].unique()), 
                         multi=True, style={'color': 'black'})
        ], style={'width': '35%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label("Período de Análise:", style={'display': 'block'}),
            dcc.DatePickerRange(
                id='filtro-data', min_date_allowed=data_min, max_date_allowed=data_max,
                start_date=data_min, end_date=data_max, display_format='DD/MM/YYYY'
            )
        ], style={'width': '40%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Button('🔄 Resetar Filtros', id='btn-reset', n_clicks=0, 
                        style={'marginTop': '20px', 'backgroundColor': '#ff4b4b', 'color': 'white', 'border': 'none', 'padding': '10px 15px', 'borderRadius': '5px', 'cursor': 'pointer', 'fontWeight': 'bold'})
        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'right', 'verticalAlign': 'top'})
    ], style={'backgroundColor': '#111', 'borderRadius': '10px', 'padding': '10px', 'marginBottom': '20px'}),

    html.Div([
        html.Div([html.H5("Faturamento Total", style={'color': '#aaa', 'margin': '0'}), html.H3(id='kpi-faturamento', style={'margin': '10px 0', 'color': '#00d4ff'})], style=kpi_style),
        html.Div([html.H5("Ticket Médio", style={'color': '#aaa', 'margin': '0'}), html.H3(id='kpi-ticket', style={'margin': '10px 0'})], style=kpi_style),
        html.Div([html.H5("Nota Média (1-5)", style={'color': '#aaa', 'margin': '0'}), html.H3(id='kpi-nota', style={'margin': '10px 0', 'color': '#ffea00'})], style=kpi_style),
        html.Div([html.H5("Custo Total Frete", style={'color': '#aaa', 'margin': '0'}), html.H3(id='kpi-frete', style={'margin': '10px 0', 'color': '#ff4b4b'})], style=kpi_style),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    dcc.Graph(id='grafico-linha-ia'),

    html.Div([
        dcc.Graph(id='grafico-canais', style={'width': '33%'}),
        dcc.Graph(id='grafico-estados', style={'width': '33%'}),
        dcc.Graph(id='grafico-vendedores', style={'width': '34%'})
    ], style={'display': 'flex', 'marginTop': '15px'})
])

@app.callback(
    [Output('grafico-linha-ia', 'figure'),
     Output('grafico-canais', 'figure'),
     Output('grafico-estados', 'figure'),
     Output('grafico-vendedores', 'figure'),
     Output('kpi-faturamento', 'children'),
     Output('kpi-ticket', 'children'),
     Output('kpi-nota', 'children'),
     Output('kpi-frete', 'children')],
    [Input('filtro-categoria', 'value'),
     Input('filtro-data', 'start_date'),
     Input('filtro-data', 'end_date'),
     Input('grafico-canais', 'clickData'),
     Input('btn-reset', 'n_clicks')]
)
def atualizar_dashboard(categoria_sel, start_date, end_date, click_canal, n_reset):
    trigger = ctx.triggered_id
    
    if not categoria_sel: categoria_sel = []
    elif isinstance(categoria_sel, str): categoria_sel = [categoria_sel]

    df_f = df_master[(df_master['Data_Venda'] >= start_date) & (df_master['Data_Venda'] <= end_date)]
    df_f = df_f[df_f['Nome_Categoria'].isin(categoria_sel)]
    
    if df_f.empty:
        vazio = go.Figure()
        return vazio, vazio, vazio, vazio, "R$ 0", "R$ 0", "0.0 ⭐", "R$ 0"

    canal_sel = None
    if trigger == 'btn-reset': click_canal = None 
        
    if click_canal and trigger != 'btn-reset':
        canal_sel = click_canal['points'][0]['y']
        df_f = df_f[df_f['Nome_Canal'] == canal_sel]

    faturamento = df_f['Faturamento'].sum()
    qtde = df_f['Quantidade'].sum()
    frete_total = df_f['Valor_Frete'].sum()
    nota_media = df_f['Nota_Avaliacao'].mean()

    str_fat = f"R$ {faturamento:,.0f}".replace(',', '.')
    str_ticket = f"R$ {(faturamento / qtde):,.0f}".replace(',', '.') if qtde > 0 else "R$ 0"
    str_frete = f"R$ {frete_total:,.0f}".replace(',', '.')
    str_nota = f"{nota_media:.1f} ⭐"

    mensal = df_f.resample('ME', on='Data_Venda')['Faturamento'].sum().reset_index()
    if len(mensal) > 2:
        mensal['Mes'], mensal['Ano'] = mensal['Data_Venda'].dt.month, mensal['Data_Venda'].dt.year
        X, y = mensal[['Mes', 'Ano']].values, mensal['Faturamento'].values
        modelo = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, y)
        
        fut_dates = pd.date_range(start=mensal['Data_Venda'].iloc[-1], periods=13, freq='ME')[1:]
        X_fut = np.array([[d.month, d.year] for d in fut_dates])
        prevs = modelo.predict(X_fut)
    else:
        fut_dates, prevs = [], []

    fig_ia = go.Figure()
    fig_ia.add_trace(go.Scatter(x=mensal['Data_Venda'], y=mensal['Faturamento'], name='Real', mode='lines+markers', line=dict(color='#00d4ff', width=3)))
    if len(prevs) > 0:
        fig_ia.add_trace(go.Scatter(x=fut_dates, y=prevs, name='Previsão IA', line=dict(dash='dash', color='#00ff88', width=3), mode='lines+markers'))
    
    titulo_ia = f"Previsão de Faturamento" + (f" - Canal: {canal_sel}" if canal_sel else "")
    fig_ia.update_layout(title=titulo_ia, template="plotly_dark", height=350, margin=dict(t=40, b=20))

    df_canais = df_master[(df_master['Data_Venda'] >= start_date) & (df_master['Data_Venda'] <= end_date)]
    df_canais = df_canais[df_canais['Nome_Categoria'].isin(categoria_sel)]
    
    agrup_canais = df_canais.groupby('Nome_Canal')['Faturamento'].sum().reset_index().sort_values('Faturamento')
    cores_canais = ['#00d4ff' if c != canal_sel else '#ffea00' for c in agrup_canais['Nome_Canal']]
    
    fig_canais = go.Figure(go.Bar(x=agrup_canais['Faturamento'], y=agrup_canais['Nome_Canal'], orientation='h', marker_color=cores_canais))
    fig_canais.update_layout(title="Marketing (Clique p/ Filtrar)", template="plotly_dark", clickmode='event+select', margin=dict(t=40, l=100))

    agrup_estados = df_f.groupby('UF_Destino')['Faturamento'].sum().reset_index().sort_values('Faturamento', ascending=False).head(7)
    fig_estados = go.Figure(go.Bar(x=agrup_estados['UF_Destino'], y=agrup_estados['Faturamento'], marker_color='#9d00ff'))
    fig_estados.update_layout(title="Top 7 Estados (Faturamento)", template="plotly_dark", margin=dict(t=40))

    agrup_vend = df_f.groupby('Nome_Vendedor')['Faturamento'].sum().reset_index().sort_values('Faturamento')
    fig_vend = go.Figure(go.Bar(x=agrup_vend['Faturamento'], y=agrup_vend['Nome_Vendedor'], orientation='h', marker_color='#ff4b4b'))
    fig_vend.update_layout(title="Performance Vendedores", template="plotly_dark", margin=dict(t=40, l=100))

    return fig_ia, fig_canais, fig_estados, fig_vend, str_fat, str_ticket, str_nota, str_frete

if __name__ == '__main__':
    app.run(debug=True, port=8050)
