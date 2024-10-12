import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import re

# Definir o nickname do jogador
player_nickname = 'pd_freire'

# Configuração da página
st.set_page_config(
   page_title="Dashboard Interativo de Xadrez",
   page_icon="♟️",
   layout="wide",
   initial_sidebar_state="expanded",
)

# Adiciona um título
st.title("DASHBOARD INTERATIVO DE XADREZ")

# Acessa dos dados
game_info_df = pd.read_parquet("game_info_df.parquet")
openings_df = pd.read_parquet("openings_df.parquet")
df = pd.read_parquet("game_info_with_openings.parquet")
moves_df = pd.read_parquet('moves_short.parquet')

# Filtrando registros para os novos dataframes
bullet_df = df[df['event'].str.contains(r'\b[Bb]ullet\b', na=False, regex=True)]
blitz_df = df[df['event'].str.contains(r'\b[Bb]litz\b', na=False, regex=True)]
rapid_df = df[df['event'].str.contains(r'\b[Rr]apid\b', na=False, regex=True)]
correspondence_df = df[df['event'].str.contains(r'\b[Cc]orrespondence\b', na=False, regex=True)]

# Gráficos da aba 1: "Performance Geral"
# Modificando bullet_df
lista_elo_bullet = []

for index, row in bullet_df.iterrows():
    if row['winner'] == 'pd_freire':
        lista_elo_bullet.append(row['winner_elo'])
    else:
        lista_elo_bullet.append(row['loser_elo'])

bullet_df['elo_bullet_list'] = lista_elo_bullet

# Modificando blitz_df
lista_elo_blitz = []

for index, row in blitz_df.iterrows():
    if row['winner'] == 'pd_freire':
        lista_elo_blitz.append(row['winner_elo'])
    else:
        lista_elo_blitz.append(row['loser_elo'])

blitz_df['elo_blitz_list'] = lista_elo_blitz

# Modificando rapid_df
lista_elo_rapid = []

for index, row in rapid_df.iterrows():
    if row['winner'] == 'pd_freire':
        lista_elo_rapid.append(row['winner_elo'])
    else:
        lista_elo_rapid.append(row['loser_elo'])

rapid_df['elo_rapid_list'] = lista_elo_rapid

# Tratamento da coluna 'date_played' para o formato datetime
bullet_df.loc[:, 'date_played'] = pd.to_datetime(bullet_df['date_played'])
blitz_df.loc[:, 'date_played'] = pd.to_datetime(blitz_df['date_played'])
rapid_df.loc[:, 'date_played'] = pd.to_datetime(rapid_df['date_played'])

# Remover registros com valores NaN na coluna 'elo_xxxxx_list'
bullet_df_clean = bullet_df.dropna(subset=['elo_bullet_list']).copy()
blitz_df_clean = blitz_df.dropna(subset=['elo_blitz_list']).copy()
rapid_df_clean = rapid_df.dropna(subset=['elo_rapid_list']).copy()

# Garantir que as colunas de rating sejam numéricas
bullet_df_clean.loc[:, 'elo_bullet_list'] = pd.to_numeric(bullet_df_clean['elo_bullet_list'])
blitz_df_clean.loc[:, 'elo_blitz_list'] = pd.to_numeric(blitz_df_clean['elo_blitz_list'])
rapid_df_clean.loc[:, 'elo_rapid_list'] = pd.to_numeric(rapid_df_clean['elo_rapid_list'])

# Criando o gráfico de linha
fig_grafico_linha = go.Figure()
fig_grafico_linha.add_trace(go.Scatter(x=bullet_df_clean['date_played'], y=bullet_df_clean['elo_bullet_list'],
                         mode='lines',
                         name='Bullet',
                         line=dict(color='blue')))
fig_grafico_linha.add_trace(go.Scatter(x=blitz_df_clean['date_played'], y=blitz_df_clean['elo_blitz_list'],
                         mode='lines',
                         name='Blitz',
                         line=dict(color='green')))
fig_grafico_linha.add_trace(go.Scatter(x=rapid_df_clean['date_played'], y=rapid_df_clean['elo_rapid_list'],
                         mode='lines',
                         name='Rapid',
                         line=dict(color='red')))
fig_grafico_linha.update_yaxes(title_text='Rating', autorange=True)
fig_grafico_linha.update_xaxes(title_text='Data')
fig_grafico_linha.update_layout(title='Evolução do Rating nos Formatos Bullet, Blitz e Rapid',
                  legend_title='Formato',
                  xaxis_title='Data',
                  yaxis_title='Rating')

# Gráfico de pizza de V-D-E no bullet
bullet_df_pie = bullet_df.copy()

bullet_df_pie['outcome'] = bullet_df_pie.apply(
    lambda row: 'Vitória' if row['winner'] == player_nickname 
    else 'Empate' if row['winner'] == 'draw' 
    else 'Derrota', axis=1
)

result_counts = bullet_df_pie['outcome'].value_counts()

fig_bullet_pie = px.pie(
    values=result_counts.values,
    names=result_counts.index,
    title=f'Performance do usuário em Bullet (Vitórias, Derrotas e Empates)',
    width=700,
    height=500,
    color_discrete_sequence=['#1E90FF', '#00008B', '#ADD8E6']
)

# Gráfico de barra de V-D-E no bullet
bullet_df_bar = bullet_df.copy()

bullet_df_bar['outcome'] = bullet_df_bar.apply(
    lambda row: 'Vitória' if row['winner'] == player_nickname 
    else 'Empate' if row['winner'] == 'draw' 
    else 'Derrota', axis=1
)

result_counts = bullet_df_bar['outcome'].value_counts().reset_index()
result_counts.columns = ['Resultado', 'Quantidade']

fig_bullet_bar = px.bar(
    result_counts,
    x='Resultado',
    y='Quantidade',
    width=700,
    height=500,
    title=f'Performance do usuário em Bullet (Vitórias, Derrotas e Empates)',
    color='Resultado',
    color_discrete_sequence=['#1E90FF', '#00008B', '#ADD8E6']
)

fig_bullet_bar.update_layout(xaxis_title='Resultado', yaxis_title='Quantidade')


# Gráfico de pizza de V-D-E no blitz
blitz_df_pie = blitz_df.copy()

blitz_df_pie['outcome'] = blitz_df_pie.apply(
    lambda row: 'Vitória' if row['winner'] == player_nickname 
    else 'Empate' if row['winner'] == 'draw' 
    else 'Derrota', axis=1
)

result_counts = blitz_df_pie['outcome'].value_counts()

fig_blitz_pie = px.pie(
    values=result_counts.values,
    names=result_counts.index,
    title=f'Performance do usuário em Blitz (Vitórias, Derrotas e Empates)',
    width=700,
    height=500,
    color_discrete_sequence=['#00008B', '#1E90FF', '#ADD8E6']
)

# Gráfico de barras V-D-E no blitz
blitz_df_bar = blitz_df.copy()

blitz_df_bar['outcome'] = blitz_df_bar.apply(
    lambda row: 'Vitória' if row['winner'] == player_nickname 
    else 'Empate' if row['winner'] == 'draw' 
    else 'Derrota', axis=1
)

result_counts = blitz_df_bar['outcome'].value_counts().reset_index()
result_counts.columns = ['Resultado', 'Quantidade']

fig_blitz_bar = px.bar(
    result_counts,
    x='Resultado',
    y='Quantidade',
    width=700,
    height=500,
    title=f'Performance do usuário em Blitz (Vitórias, Derrotas e Empates)',
    color='Resultado',
    color_discrete_sequence=['#00008B', '#1E90FF', '#ADD8E6']
)

fig_blitz_bar.update_layout(xaxis_title='Resultado', yaxis_title='Quantidade')

# Gráfico de pizza V-D-E em rapid
rapid_df_pie = rapid_df.copy()

rapid_df_pie['outcome'] = rapid_df_pie.apply(
    lambda row: 'Vitória' if row['winner'] == player_nickname 
    else 'Empate' if row['winner'] == 'draw' 
    else 'Derrota', axis=1
)

result_counts = rapid_df_pie['outcome'].value_counts()

fig_rapid_pie = px.pie(
    values=result_counts.values,
    names=result_counts.index,
    title=f'Performance do usuário em Rápidas (Vitórias, Derrotas e Empates)',
    width=700,
    height=500,
    color_discrete_sequence=['#1E90FF', '#00008B', '#ADD8E6']
)

# Gráfico de barras V-D-E em rapid
rapid_df_bar = rapid_df.copy()

rapid_df_bar['outcome'] = rapid_df_bar.apply(
    lambda row: 'Vitória' if row['winner'] == player_nickname 
    else 'Empate' if row['winner'] == 'draw' 
    else 'Derrota', axis=1
)

result_counts = rapid_df_bar['outcome'].value_counts().reset_index()
result_counts.columns = ['Resultado', 'Quantidade']

fig_rapid_bar = px.bar(
    result_counts,
    x='Resultado',
    y='Quantidade',
    width=700,
    height=500,
    title=f'Performance do usuário em Rápidas (Vitórias, Derrotas e Empates)',
    color='Resultado',
    color_discrete_sequence=['#1E90FF', '#00008B', '#ADD8E6']
)

fig_rapid_bar.update_layout(xaxis_title='Resultado', yaxis_title='Quantidade')

# Diagrama Sankey
df['outcome'] = df['winner'].apply(
    lambda x: 'Vitória' if x == 'pd_freire' 
    else 'Empate' if x == 'draw' 
    else 'Derrota'
)

df_filtered = df[df['outcome'].isin(['Vitória', 'Derrota'])].copy()
df_filtered['termination_event'] = df_filtered.apply(lambda row: f"{row['termination']} ({row['outcome']})", axis=1)

termination_event_counts = df_filtered.groupby(['termination_event', 'event']).size().reset_index(name='count')

labels = [
    'Partidas Totais',                 # Index 0
    'Vitória',                         # Index 1
    'Derrota',                         # Index 2
    'Time forfeit (Vitória)',          # Index 3
    'Normal (Vitória)',                # Index 4
    'Abandoned (Vitória)',             # Index 5
    'Time forfeit (Derrota)',          # Index 6
    'Normal (Derrota)'                 # Index 7
]

event_labels = list(termination_event_counts['event'].unique())
labels.extend(event_labels)

source = [
    0, 0,  
    1, 1, 1, 
    2, 2      
]

target = [
    1, 2,  
    3, 4, 5,  
    6, 7      
]

value = [
    df_filtered[df_filtered['outcome'] == 'Vitória'].shape[0], 
    df_filtered[df_filtered['outcome'] == 'Derrota'].shape[0],
    df_filtered[(df_filtered['outcome'] == 'Vitória') & (df_filtered['termination'] == 'Time forfeit')].shape[0],
    df_filtered[(df_filtered['outcome'] == 'Vitória') & (df_filtered['termination'] == 'Normal')].shape[0],
    df_filtered[(df_filtered['outcome'] == 'Vitória') & (df_filtered['termination'] == 'Abandoned')].shape[0],
    df_filtered[(df_filtered['outcome'] == 'Derrota') & (df_filtered['termination'] == 'Time forfeit')].shape[0],
    df_filtered[(df_filtered['outcome'] == 'Derrota') & (df_filtered['termination'] == 'Normal')].shape[0]
]

for index, row in termination_event_counts.iterrows():
    termination_event_label = row['termination_event']
    event_label = row['event']
    
    termination_index = labels.index(termination_event_label)
    event_index = labels.index(event_label)
    
    source.append(termination_index)
    target.append(event_index)
    value.append(row['count'])

fig_sankey = go.Figure(go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color=["gray", "#00008B", "#1E90FF", "#00008B", "#00008B", "#00008B", "#1E90FF", "#1E90FF"] + ["lightgreen"] * len(event_labels)
    ),
    link=dict(
        source=source,
        target=target,
        value=value
    )
))

fig_sankey.update_layout(
    title_text="Diagrama Sankey com subdivisões dos jogos",
    font_size=12,
    width=1100,
    height=800
)

# Gráfico dos horários
df['utc_time'] = pd.to_datetime(df['utc_time'], format='%H:%M:%S').dt.time

def categorize_time(hour):
    if hour >= pd.to_datetime('00:01').time() and hour <= pd.to_datetime('06:00').time():
        return 'Madrugada'
    elif hour > pd.to_datetime('06:00').time() and hour <= pd.to_datetime('12:00').time():
        return 'Manhã'
    elif hour > pd.to_datetime('12:00').time() and hour <= pd.to_datetime('18:00').time():
        return 'Tarde'
    else:
        return 'Noite'

df['period'] = df['utc_time'].apply(lambda x: categorize_time(x))

def categorize_result(row):
    if row['winner'] == 'pd_freire':
        return 'Vitória'
    elif row['winner'] == 'draw':
        return 'Empate'
    else:
        return 'Derrota'

df['result'] = df.apply(categorize_result, axis=1)

result_counts = df.groupby(['period', 'result']).size().unstack(fill_value=0)
result_counts = result_counts.reindex(columns=['Vitória', 'Empate', 'Derrota'], fill_value=0)

period_order = ['Madrugada', 'Manhã', 'Tarde', 'Noite']
result_counts = result_counts.reindex(period_order)

fig_horarios = px.bar(result_counts, 
             barmode='stack',
             width=700,
             height=500,
             title='Quantidade de Vitórias, Derrotas e Empates por Período do Dia',
             labels={'value': 'Quantidade', 'period': 'Período do Dia'},
             color_discrete_sequence=['#00008B', '#ADD8E6', '#1E90FF'])

fig_horarios.update_layout(xaxis_title='Período do Dia', 
                  yaxis_title='Quantidade', 
                  legend_title='Resultados')


# 2 Análise de Aberturas
# Criando o dataframe 'df_white' com jogos onde 'pd_freire' jogou com as peças brancas
df_white = df[df['white'] == 'pd_freire'].copy()

# Criando o dataframe 'df_black' com jogos onde 'pd_freire' jogou com as peças pretas
df_black = df[df['black'] == 'pd_freire'].copy()

# Criar a coluna 'general_opening' com o conteúdo da coluna 'opening' até a primeira vírgula, sem incluir a vírgula
df_white['general_opening'] = df_white['opening'].str.extract(r'([^,]+)', expand=False)
df_black['general_opening'] = df_black['opening'].str.extract(r'([^,]+)', expand=False)

# Aberturas que mais ocorreram jogando com as brancas
top_openings = df_white['general_opening'].value_counts().nlargest(10)
top_openings_list = top_openings.index.tolist()

top_openings_df = df_white[df_white['general_opening'].isin(top_openings_list)].copy()

top_openings_df.loc[:, 'result'] = top_openings_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts = top_openings_df.groupby(['general_opening', 'result']).size().reset_index(name='count')

total_counts = top_openings_df['general_opening'].value_counts().nlargest(10).reset_index()
total_counts.columns = ['general_opening', 'total_count']
result_counts = result_counts.merge(total_counts, on='general_opening')
result_counts = result_counts.sort_values(by='total_count', ascending=False)

fig_white_opening = px.bar(result_counts, 
             x='count', 
             y='general_opening', 
             color='result', 
             orientation='h', 
             title='Resultados das 10 aberturas que mais ocorreram quando o usuário jogou de brancas',
             labels={'count':'Quantidade de Jogos', 'general_opening':'Abertura', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_white_opening.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Abertura',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'} 
)

# Aberturas que mais ocorreram jogando com as pretas
top_openings_black = df_black['general_opening'].value_counts().nlargest(10)
top_openings_black_list = top_openings_black.index.tolist()
top_openings_black_df = df_black[df_black['general_opening'].isin(top_openings_black_list)].copy()
top_openings_black_df.loc[:, 'result'] = top_openings_black_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts_black = top_openings_black_df.groupby(['general_opening', 'result']).size().reset_index(name='count')
total_counts_black = top_openings_black_df['general_opening'].value_counts().nlargest(10).reset_index()
total_counts_black.columns = ['general_opening', 'total_count']
result_counts_black = result_counts_black.merge(total_counts_black, on='general_opening')
result_counts_black = result_counts_black.sort_values(by='total_count', ascending=False)

fig_black_opening = px.bar(result_counts_black, 
             x='count', 
             y='general_opening', 
             color='result', 
             orientation='h', 
             title='Resultados das 10 aberturas que mais ocorreram quando o usuário jogou de pretas',
             labels={'count':'Quantidade de Jogos', 'general_opening':'Abertura', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_black_opening.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Abertura',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'}
)

# Variantes mais jogadas das aberturas (French Defense / Brancas)
french_defense_df = df_white[df_white['general_opening'] == 'French Defense'].copy()
french_defense_df['variation'] = french_defense_df['opening'].apply(lambda x: re.split(r',\s*', x)[1] if ',' in x else 'Unknown')

top_variations = french_defense_df['variation'].value_counts().nlargest(5)
top_variations_list = top_variations.index.tolist()
top_variations_df = french_defense_df[french_defense_df['variation'].isin(top_variations_list)].copy()

top_variations_df.loc[:, 'result'] = top_variations_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts_variations = top_variations_df.groupby(['variation', 'result']).size().reset_index(name='count')
total_counts_variations = top_variations_df['variation'].value_counts().nlargest(5).reset_index()
total_counts_variations.columns = ['variation', 'total_count']
result_counts_variations = result_counts_variations.merge(total_counts_variations, on='variation')
result_counts_variations = result_counts_variations.sort_values(by='total_count', ascending=False)

fig_white_french = px.bar(result_counts_variations, 
             x='count', 
             y='variation', 
             color='result', 
             orientation='h', 
             title='Resultados das 5 Principais Variações da French Defense Enfrentadas pelo Jogador (Brancas)',
             labels={'count':'Quantidade de Jogos', 'variation':'Variação', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_white_french.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Variação',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'}
)

# Variantes mais jogadas das aberturas (English Opening / Brancas)
english_opening_df = df_white[df_white['general_opening'] == 'English Opening'].copy()
english_opening_df['variation'] = english_opening_df['opening'].apply(lambda x: re.split(r',\s*', x)[1] if ',' in x else 'Unknown')

top_variations = english_opening_df['variation'].value_counts().nlargest(5)
top_variations_list = top_variations.index.tolist()
top_variations_df = english_opening_df[english_opening_df['variation'].isin(top_variations_list)].copy()
top_variations_df.loc[:, 'result'] = top_variations_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts_variations = top_variations_df.groupby(['variation', 'result']).size().reset_index(name='count')
total_counts_variations = top_variations_df['variation'].value_counts().nlargest(5).reset_index()
total_counts_variations.columns = ['variation', 'total_count']
result_counts_variations = result_counts_variations.merge(total_counts_variations, on='variation')
result_counts_variations = result_counts_variations.sort_values(by='total_count', ascending=False)

fig_white_english = px.bar(result_counts_variations, 
             x='count', 
             y='variation', 
             color='result', 
             orientation='h', 
             title='Resultados das 5 Principais Variações da English Opening Enfrentadas pelo Jogador (Brancas)',
             labels={'count':'Quantidade de Jogos', 'variation':'Variação', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_white_english.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Variação',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'} 
)

# Variantes mais jogadas das aberturas (Zukertort Opening / Brancas)
zukertort_opening_df = df_white[df_white['general_opening'] == 'Zukertort Opening'].copy()
zukertort_opening_df['variation'] = zukertort_opening_df['opening'].apply(lambda x: re.split(r',\s*', x)[1] if ',' in x else 'Unknown')

top_variations = zukertort_opening_df['variation'].value_counts().nlargest(5)
top_variations_list = top_variations.index.tolist()
top_variations_df = zukertort_opening_df[zukertort_opening_df['variation'].isin(top_variations_list)].copy()
top_variations_df.loc[:, 'result'] = top_variations_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts_variations = top_variations_df.groupby(['variation', 'result']).size().reset_index(name='count')
total_counts_variations = top_variations_df['variation'].value_counts().nlargest(5).reset_index()
total_counts_variations.columns = ['variation', 'total_count']
result_counts_variations = result_counts_variations.merge(total_counts_variations, on='variation')
result_counts_variations = result_counts_variations.sort_values(by='total_count', ascending=False)

fig_white_zukertort = px.bar(result_counts_variations, 
             x='count', 
             y='variation', 
             color='result', 
             orientation='h', 
             title='Resultados das 5 Principais Variações da Zukertort Opening Enfrentadas pelo Jogador (Brancas)',
             labels={'count':'Quantidade de Jogos', 'variation':'Variação', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_white_zukertort.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Variação',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'}
)

# Variantes mais jogadas das aberturas (Sicilian Defense / Brancas)
sicilian_defense_df = df_white[df_white['general_opening'] == 'Sicilian Defense'].copy()

sicilian_defense_df['variation'] = sicilian_defense_df['opening'].apply(lambda x: re.split(r',\s*', x)[1] if ',' in x else 'Unknown')
top_variations = sicilian_defense_df['variation'].value_counts().nlargest(5)
top_variations_list = top_variations.index.tolist()
top_variations_df = sicilian_defense_df[sicilian_defense_df['variation'].isin(top_variations_list)].copy()
top_variations_df.loc[:, 'result'] = top_variations_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts_variations = top_variations_df.groupby(['variation', 'result']).size().reset_index(name='count')
total_counts_variations = top_variations_df['variation'].value_counts().nlargest(5).reset_index()
total_counts_variations.columns = ['variation', 'total_count']
result_counts_variations = result_counts_variations.merge(total_counts_variations, on='variation')
result_counts_variations = result_counts_variations.sort_values(by='total_count', ascending=False)

fig_white_sicilian = px.bar(result_counts_variations, 
             x='count', 
             y='variation', 
             color='result', 
             orientation='h', 
             title='Resultados das 5 Principais Variações da Sicilian Defense Enfrentadas pelo Jogador (Brancas)',
             labels={'count':'Quantidade de Jogos', 'variation':'Variação', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_white_sicilian.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Variação',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'} 
)

# Variantes mais jogadas das aberturas (French Defense / Pretas)
french_defense_black_df = df_black[df_black['general_opening'] == 'French Defense'].copy()

french_defense_black_df['variation'] = french_defense_black_df['opening'].apply(lambda x: re.split(r',\s*', x)[1] if ',' in x else 'Unknown')
top_variations_black = french_defense_black_df['variation'].value_counts().nlargest(5)
top_variations_black_list = top_variations_black.index.tolist()
top_variations_black_df = french_defense_black_df[french_defense_black_df['variation'].isin(top_variations_black_list)].copy()
top_variations_black_df.loc[:, 'result'] = top_variations_black_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts_variations_black = top_variations_black_df.groupby(['variation', 'result']).size().reset_index(name='count')
total_counts_variations_black = top_variations_black_df['variation'].value_counts().nlargest(5).reset_index()
total_counts_variations_black.columns = ['variation', 'total_count']
result_counts_variations_black = result_counts_variations_black.merge(total_counts_variations_black, on='variation')
result_counts_variations_black = result_counts_variations_black.sort_values(by='total_count', ascending=False)

fig_black_french = px.bar(result_counts_variations_black, 
             x='count', 
             y='variation', 
             color='result', 
             orientation='h', 
             title='Resultados das 5 Principais Variações da French Defense Enfrentadas pelo Jogador (Pretas)',
             labels={'count':'Quantidade de Jogos', 'variation':'Variação', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_black_french.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Variação',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'} 
)

# Variantes mais jogadas das aberturas (English Opening / Pretas)
english_opening_black_df = df_black[df_black['general_opening'] == 'English Opening'].copy()

english_opening_black_df['variation'] = english_opening_black_df['opening'].apply(lambda x: re.split(r',\s*', x)[1] if ',' in x else 'Unknown')
top_variations_black = english_opening_black_df['variation'].value_counts().nlargest(5)
top_variations_black_list = top_variations_black.index.tolist()
top_variations_black_df = english_opening_black_df[english_opening_black_df['variation'].isin(top_variations_black_list)].copy()
top_variations_black_df.loc[:, 'result'] = top_variations_black_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts_variations_black = top_variations_black_df.groupby(['variation', 'result']).size().reset_index(name='count')
total_counts_variations_black = top_variations_black_df['variation'].value_counts().nlargest(5).reset_index()
total_counts_variations_black.columns = ['variation', 'total_count']
result_counts_variations_black = result_counts_variations_black.merge(total_counts_variations_black, on='variation')
result_counts_variations_black = result_counts_variations_black.sort_values(by='total_count', ascending=False)

fig_black_english = px.bar(result_counts_variations_black, 
             x='count', 
             y='variation', 
             color='result', 
             orientation='h', 
             title='Resultados das 5 Principais Variações da English Opening Enfrentadas pelo Jogador (Pretas)',
             labels={'count':'Quantidade de Jogos', 'variation':'Variação', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_black_english.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Variação',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'}
)

# Variantes mais jogadas das aberturas (Zukertort Opening / Pretas)
zukertort_opening_black_df = df_black[df_black['general_opening'] == 'Zukertort Opening'].copy()

zukertort_opening_black_df['variation'] = zukertort_opening_black_df['opening'].apply(lambda x: re.split(r',\s*', x)[1] if ',' in x else 'Unknown')
top_variations_black = zukertort_opening_black_df['variation'].value_counts().nlargest(5)
top_variations_black_list = top_variations_black.index.tolist()
top_variations_black_df = zukertort_opening_black_df[zukertort_opening_black_df['variation'].isin(top_variations_black_list)].copy()
top_variations_black_df.loc[:, 'result'] = top_variations_black_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts_variations_black = top_variations_black_df.groupby(['variation', 'result']).size().reset_index(name='count')
total_counts_variations_black = top_variations_black_df['variation'].value_counts().nlargest(5).reset_index()
total_counts_variations_black.columns = ['variation', 'total_count']
result_counts_variations_black = result_counts_variations_black.merge(total_counts_variations_black, on='variation')
result_counts_variations_black = result_counts_variations_black.sort_values(by='total_count', ascending=False)

fig_black_zukertort = px.bar(result_counts_variations_black, 
             x='count', 
             y='variation', 
             color='result', 
             orientation='h', 
             title='Resultados das 5 Principais Variações da Zukertort Opening Enfrentadas pelo Jogador (Pretas)',
             labels={'count':'Quantidade de Jogos', 'variation':'Variação', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_black_zukertort.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Variação',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'} 
)

# Variantes mais jogadas das aberturas (Sicilian Defense / Pretas)
sicilian_defense_black_df = df_black[df_black['general_opening'] == 'Sicilian Defense'].copy()

sicilian_defense_black_df['variation'] = sicilian_defense_black_df['opening'].apply(lambda x: re.split(r',\s*', x)[1] if ',' in x else 'Unknown')
top_variations_black = sicilian_defense_black_df['variation'].value_counts().nlargest(5)
top_variations_black_list = top_variations_black.index.tolist()
top_variations_black_df = sicilian_defense_black_df[sicilian_defense_black_df['variation'].isin(top_variations_black_list)].copy()
top_variations_black_df.loc[:, 'result'] = top_variations_black_df.apply(
    lambda row: 'Vitória' if row['winner'] == 'pd_freire' else (
        'Empate' if row['winner'] == 'draw' else 'Derrota'),
    axis=1
)

result_counts_variations_black = top_variations_black_df.groupby(['variation', 'result']).size().reset_index(name='count')
total_counts_variations_black = top_variations_black_df['variation'].value_counts().nlargest(5).reset_index()
total_counts_variations_black.columns = ['variation', 'total_count']
result_counts_variations_black = result_counts_variations_black.merge(total_counts_variations_black, on='variation')
result_counts_variations_black = result_counts_variations_black.sort_values(by='total_count', ascending=False)

fig_black_sicilian = px.bar(result_counts_variations_black, 
             x='count', 
             y='variation', 
             color='result', 
             orientation='h', 
             title='Resultados das 5 Principais Variações da Sicilian Defense Enfrentadas pelo Jogador (Pretas)',
             labels={'count':'Quantidade de Jogos', 'variation':'Variação', 'result':'Resultado'},
             color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'})

fig_black_sicilian.update_layout(
    width=1600,
    xaxis_title='Quantidade de Jogos',
    yaxis_title='Variação',
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'} 
)

# 3 Análise Tática e Estratégica

# 3.1 Número de lances por jogo
merged_df = pd.merge(df, moves_df, on='game_id')

def classify_result(row):
    if row['winner'] == 'pd_freire':
        return 'Vitória'
    elif row['winner'] == 'draw':
        return 'Empate'
    else:
        return 'Derrota'

merged_df['result'] = merged_df.apply(classify_result, axis=1)
game_moves_count = merged_df.groupby(['game_id', 'result'])['move_no'].max().reset_index()

fig_moves_number = px.histogram(game_moves_count, 
                   x='move_no', 
                   color='result', 
                   nbins=20,
                   title='Distribuição da quantidade de lances por jogo',
                   labels={'move_no': 'Número de Lances', 'count': 'Quantidade de Jogos', 'result': 'Resultado'},
                   color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF', 'Empate': '#ADD8E6'}
)

fig_moves_number.update_layout(
    width=900, 
    height=600,
    xaxis_title='Número de Lances',
    yaxis_title='Quantidade de Jogos',
    barmode='stack',
    bargap=0.1
)

# 3.2 Jogos decididos em menos de 20 lances (abertura)
games_less_than_20_moves = merged_df.groupby('game_id').filter(lambda x: x['move_no'].max() < 21)
games_less_than_20_moves['result'] = games_less_than_20_moves.apply(classify_result, axis=1)

decisive_games = games_less_than_20_moves[games_less_than_20_moves['result'] != 'Empate']

decisive_games_count = decisive_games.groupby(['game_id', 'result']).size().reset_index(name='count')

total_victories = decisive_games[decisive_games['result'] == 'Vitória'].game_id.nunique()
total_defeats = decisive_games[decisive_games['result'] == 'Derrota'].game_id.nunique()

fig_less_20_moves = px.scatter(decisive_games_count, 
                 x=decisive_games_count.index, 
                 y='count', 
                 color='result',
                 title=f'Jogos decididos com menos de 20 lances (Vitórias: {total_victories}, Derrotas: {total_defeats})',
                 labels={'count': 'Quantidade de lances', 'result': 'Resultado'},
                 color_discrete_map={'Vitória': '#00008B', 'Derrota': '#1E90FF'}
)

fig_less_20_moves.update_layout(
    width=1000, 
    height=600,
    xaxis_title=None,
    xaxis_showticklabels=False
)

# 3.3 Casas mais ocupadas pelo usuário
df_white = df[df['white'] == 'pd_freire'].copy()
df_black = df[df['black'] == 'pd_freire'].copy()

# Casas mais ocupadas quando o usuário joga com as brancas
df_white_moves = pd.merge(df_white, moves_df, on='game_id')
df_white_moves = df_white_moves[df_white_moves['color'] == 'White']

df_white_moves['file'] = df_white_moves['to_square'].apply(lambda x: re.match(r'([a-h])\d', x).group(1))
df_white_moves['rank'] = df_white_moves['to_square'].apply(lambda x: re.match(r'[a-h](\d)', x).group(1))

df_white_moves['rank'] = df_white_moves['rank'].astype(int)

heatmap_data = df_white_moves.pivot_table(index='rank', columns='file', aggfunc='size', fill_value=0)

fig_white_occupy = px.imshow(heatmap_data, 
                labels=dict(x='Coluna (File)', y='Linha (Rank)', color='Número de Movimentos'),
                title = 'Casas mais ocupadas quando o usuário joga com as brancas',
                x=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                y=[1, 2, 3, 4, 5, 6, 7, 8],
                color_continuous_scale='Blues')

fig_white_occupy.update_layout(
    yaxis=dict(autorange=True),
    width=600,  
    height=600 
)

# Casas mais ocupadas quando o usuário joga com as pretas
df_black_moves = pd.merge(df_black, moves_df, on='game_id')
df_black_moves = df_black_moves[df_black_moves['color'] == 'Black']

df_black_moves['file'] = df_black_moves['to_square'].apply(lambda x: re.match(r'([a-h])\d', x).group(1))
df_black_moves['rank'] = df_black_moves['to_square'].apply(lambda x: re.match(r'[a-h](\d)', x).group(1))

df_black_moves['rank'] = df_black_moves['rank'].astype(int)

heatmap_data = df_black_moves.pivot_table(index='rank', columns='file', aggfunc='size', fill_value=0)

fig_black_occupy = px.imshow(heatmap_data, 
                labels=dict(x='Coluna (File)', y='Linha (Rank)', color='Número de Movimentos'),
                title = 'Casas mais ocupadas quando o usuário joga com as pretas',
                x=['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a'],
                y=[1, 2, 3, 4, 5, 6, 7, 8],
                color_continuous_scale='Blues')

fig_black_occupy.update_layout(
    yaxis=dict(autorange="reversed"),
    width=600,  
    height=600  
)

# 3.4 Tipo de peça usada para o xeque-mate
# Quando o usuário aplicou xeque-mate
winning_games_df = df[df['winner'] == 'pd_freire']

check_mates_moves_df = moves_df[moves_df['is_check_mate'] == 1]

check_mates_df = pd.merge(check_mates_moves_df, winning_games_df, on='game_id', how='inner')

check_mates_by_piece = check_mates_df['piece'].value_counts().reset_index()
check_mates_by_piece.columns = ['piece', 'count']

piece_names = {
    'Q': 'Dama',
    'R': 'Torre',
    'B': 'Bispo',
    'N': 'Cavalo',
    'P': 'Peão'
}

check_mates_by_piece['piece'] = check_mates_by_piece['piece'].map(piece_names)

fig_mate_given = px.bar(check_mates_by_piece, 
             x='piece', 
             y='count', 
             title='Tipos de peça usadas pelo usuário para aplicar xeque-mate',
             labels={'piece': 'Peça', 'count': 'Quantidade de Xeque-mates'},
             color_discrete_sequence=['#00008B'])

fig_mate_given.update_layout(width=800, height=400)

# Quando o usuário sofreu xeque-mate
losing_games_df = df[df['winner'] != 'pd_freire']

check_mates_moves_df = moves_df[moves_df['is_check_mate'] == 1]

check_mates_df = pd.merge(check_mates_moves_df, losing_games_df, on='game_id', how='inner')

check_mates_by_piece = check_mates_df['piece'].value_counts().reset_index()
check_mates_by_piece.columns = ['piece', 'count']

check_mates_by_piece['piece'] = check_mates_by_piece['piece'].map(piece_names)

fig_mate_taken = px.bar(check_mates_by_piece, 
             x='piece', 
             y='count', 
             title='Tipos de peça usadas pelos adversários para aplicar xeque-mate no usuário',
             labels={'piece': 'Peça', 'count': 'Quantidade de Xeque-mates'},
             color_discrete_sequence=['#00008B'])

fig_mate_taken.update_layout(width=800, height=400)

# 3.6 Xeque-mates por abertura
# Xeque-mates aplicados pelo usuário
winning_games_df = df[df['winner'] == 'pd_freire']

check_mates_moves_df = moves_df[moves_df['is_check_mate'] == 1]

check_mates_openings_df = pd.merge(check_mates_moves_df, winning_games_df, on='game_id', how='inner')

check_mates_by_opening = check_mates_openings_df['opening'].value_counts().nlargest(10).reset_index()
check_mates_by_opening.columns = ['opening', 'count']

fig_mate_given_opening = px.bar(check_mates_by_opening, 
             x='count', 
             y='opening', 
             orientation='h', 
             title='Top 10 aberturas em que o usuário aplicou xeque-mate',
             labels={'count': 'Quantidade de Xeque-mates', 'opening': 'Abertura'},
             color_discrete_sequence=['#00008B'])

fig_mate_given_opening.update_layout(
    width=800, 
    height=500,
    xaxis_title='Quantidade de Xeque-mates',
    yaxis_title='Abertura',
)

# Xeque-mates sofridos pelo usuário
losing_games_df = df[df['winner'] != 'pd_freire']
check_mates_moves_df = moves_df[moves_df['is_check_mate'] == 1]
check_mates_openings_df = pd.merge(check_mates_moves_df, losing_games_df, on='game_id', how='inner')
check_mates_by_opening = check_mates_openings_df['opening'].value_counts().nlargest(10).reset_index()
check_mates_by_opening.columns = ['opening', 'count']

fig_mate_taken_opening = px.bar(check_mates_by_opening, 
             x='count', 
             y='opening', 
             orientation='h', 
             title='Top 10 aberturas em que o usuário sofreu xeque-mate',
             labels={'count': 'Quantidade de Xeque-mates', 'opening': 'Abertura'},
             color_discrete_sequence=['#00008B'])

fig_mate_taken_opening.update_layout(
    width=800, 
    height=500,
    xaxis_title='Quantidade de Xeque-mates',
    yaxis_title='Abertura',
)

# 3.5 Distribuição de xeque-mates por número de lances
check_mates_df = moves_df[moves_df['is_check_mate'] == 1]

fig_mate_moves = px.histogram(check_mates_df, 
                   x='move_no', 
                   nbins=30, 
                   title='Distribuição de Xeque-mates por Número de Lances',
                   labels={'move_no': 'Número de Lances'},
                   color_discrete_sequence=['#00008B'])

fig_mate_moves.update_yaxes(title_text='Total de xeque-mates')
fig_mate_moves.update_layout(width=800, height=400)


# Organizando as abas
aba1, aba2, aba3, aba4 = st.tabs(['Performance Geral', 'Aberturas', 'Táticas e Estratégias', 'Glossário'])
with aba1:
    cabecalho1, cabecalho2 = st.columns(2)
    with cabecalho1:
        st.metric("Usuário do Lichess", 'pd_freire')
    with cabecalho2:
        st.metric("Jogos analisados", df.shape[0])
    st.plotly_chart(fig_grafico_linha, use_container_width = True)
    coluna1, coluna2, coluna3 = st.columns(3)
    with coluna1:
        st.plotly_chart(fig_bullet_pie, use_container_width = True)
        st.plotly_chart(fig_bullet_bar, use_container_width = True)
        st.plotly_chart(fig_sankey, use_container_width = False)
    with coluna2:
        st.plotly_chart(fig_blitz_pie, use_container_width = True)
        st.plotly_chart(fig_blitz_bar, use_container_width = True)
        st.plotly_chart(fig_horarios, use_container_width = True)
    with coluna3:
        st.plotly_chart(fig_rapid_pie, use_container_width = True)
        st.plotly_chart(fig_rapid_bar, use_container_width = True)
with aba2:
    cabecalho1, cabecalho2 = st.columns(2)
    with cabecalho1:
        st.metric("Usuário do Lichess", "pd_freire")
    with cabecalho2:
        st.metric("Jogos analisados", df.shape[0])
    coluna21, coluna22 = st.columns(2)
    with coluna21:
        st.plotly_chart(fig_white_opening, use_container_width = True)
        st.plotly_chart(fig_white_french, use_container_width = True)
        st.plotly_chart(fig_white_english, use_container_width = True)
        st.plotly_chart(fig_white_zukertort, use_container_width = True)
        st.plotly_chart(fig_white_sicilian, use_container_width = True)
    with coluna22:
        st.plotly_chart(fig_black_opening, use_container_width = True)
        st.plotly_chart(fig_black_french, use_container_width = True)
        st.plotly_chart(fig_black_english, use_container_width = True)
        st.plotly_chart(fig_black_zukertort, use_container_width = True)
        st.plotly_chart(fig_black_sicilian, use_container_width = True)
with aba3:
    cabecalho1, cabecalho2 = st.columns(2)
    with cabecalho1:
        st.metric("Usuário do Lichess", "pd_freire")
    with cabecalho2:
        st.metric("Jogos analisados", df.shape[0])
    coluna31, coluna32 = st.columns(2)
    with coluna31:
        st.plotly_chart(fig_moves_number, use_container_width = True)
        st.plotly_chart(fig_white_occupy, use_container_width = True)
        st.plotly_chart(fig_mate_given, use_container_width = True)
        st.plotly_chart(fig_mate_given_opening, use_container_width = True)
        st.plotly_chart(fig_mate_moves, use_container_width = True)
    with coluna32:
        st.plotly_chart(fig_less_20_moves, use_container_width = True)
        st.plotly_chart(fig_black_occupy, use_container_width = True)
        st.plotly_chart(fig_mate_taken, use_container_width = True)
        st.plotly_chart(fig_mate_taken_opening, use_container_width = True)
with aba4:
    st.markdown("**Xadrez** é um jogo de tabuleiro de estratégia para dois jogadores. O jogo é disputado em uma grade de 8x8. Cada jogador controla 16 peças: um rei, uma rainha, duas torres, dois cavalos, dois bispos e oito peões. Um jogador joga com as peças brancas e o outro com as peças pretas. O objetivo é dar xeque-mate no rei do oponente, o que significa que o rei está em posição de ser capturado e não pode escapar. Os jogadores se revezam movendo suas peças de acordo com regras específicas para cada tipo. O jogo enfatiza táticas, estratégia e previsão, tornando-o um desafio complexo e intelectualmente estimulante.")
    st.markdown("Algumas das terminologias utilizadas neste dashboard:")
    st.markdown("- **Abertura**: estágio inicial de um jogo de xadrez que consiste em teoria estabelecida por jogadores de alto nível e estudiosos ao longo do tempo. Ao jogar com com as peças brancas, o jogador tenta ganhar vantagem por ter começado primeiro e, ao jogar com as peças pretas, tenta igualar o jogo ou buscar desequilíbrios.")
    st.markdown("- **Blitz**: uma das variantes do xadrez rápido, onde os jogadores começam com menos de 10 minutos no relógio. No caso deste dashboard, as partidas de blitz são apenas em dois formatos: 3+2 (três minutos no relógio mais dois segundos de acréscimos após cada lance) e 3+0 (três minutos no relógio sem acréscimos após os lances).")
    st.markdown("- **Bullet**: uma das variantes do xadrez rápido, onde os jogadores começam com menos de 3 minutos no relógio. No caso deste dashboard, as partidas de bullet são apenas em dois formatos: 1+1 (um minuto no relógio mais um segundo de acréscimo após cada lance) e 1+0 (um minuto no relógio sem acréscimos após os lances).")
    st.markdown("- **Casa**: cada uma das 64 divisões da grade de 8x8 que compõem o tabuleiro. As casas são nomeadas pelas colunas (de 'a' a 'h') e pelas linhas (de 1 a 8). Para referenciá-las normalmente utiliza-se a notação algébrica como, por exemplo, 'e4'.")
    st.markdown("- **Rapid**: uma das variantes do xadrez rápido, onde os jogadores começam com 10 minutos ou mais no relógio e menos de 30 minutos. No caso deste dashboard, as partidas de rapid (chamadas nos gráficos de 'rápidas') são apenas em dois formatos: 15+10 (quinze minutos no relógio mais dez segundos de acréscimos após cada lance) e 10+0 (dez minutos no relógio sem acréscimos após os lances).")
    st.markdown("- **Variante**: termo usado para descrever um ramo de outra abertura nomeada, por exemplo, a 'Advance Variation' ('Variação do Avanço', em português), uma linha da 'French Defense' ('Defesa Francesa', em português).")
    st.markdown("- **Xeque-mate**: qualquer posição de jogo em que o rei de um jogador está em xeque (ameaçado de captura) e não há escapatória possível. Dar xeque-mate no oponente significa vencer o jogo.")
    