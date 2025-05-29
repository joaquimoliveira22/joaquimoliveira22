import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 👉 Digite seu nome de usuário GitHub
USERNAME = "seu_usuario"

# 👉 Opcional: coloque seu token pessoal para aumentar o limite de requisições
TOKEN = ""

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# Função para buscar os repositórios
@st.cache_data
def get_repos(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        res = requests.get(url, headers=headers)
        data = res.json()
        if not data or res.status_code != 200:
            break
        repos.extend(data)
        page += 1
    return repos

# Função para processar dados
def process_data(repos):
    df = pd.DataFrame(repos)
    df = df[['name', 'stargazers_count', 'language', 'created_at']]
    df['created_at'] = pd.to_datetime(df['created_at'])
    return df

# --- Interface Streamlit ---
st.set_page_config(page_title="GitHub Dashboard", layout="wide")
st.title("📊 GitHub Dashboard")
st.markdown(f"Estatísticas públicas de **[{USERNAME}](https://github.com/{USERNAME})**")

# --- Coleta de dados ---
with st.spinner("Carregando dados..."):
    repos = get_repos(USERNAME)

if not repos:
    st.error("Erro ao buscar dados. Verifique o nome de usuário.")
    st.stop()

df = process_data(repos)

# --- Métricas principais ---
col1, col2, col3 = st.columns(3)
col1.metric("📁 Repositórios Públicos", len(df))
col2.metric("⭐ Total de Stars", df['stargazers_count'].sum())
col3.metric("🗣️ Linguagens Usadas", df['language'].nunique())

# --- Gráfico: Linguagens mais usadas ---
lang_count = df['language'].value_counts().dropna().reset_index()
lang_count.columns = ['Linguagem', 'Repositórios']

fig1 = px.bar(lang_count, x='Linguagem', y='Repositórios', title="Linguagens mais usadas", color='Linguagem')
st.plotly_chart(fig1, use_container_width=True)

# --- Gráfico: Repositórios mais populares ---
top_repos = df.sort_values(by='stargazers_count', ascending=False).head(10)
fig2 = px.bar(top_repos, x='stargazers_count', y='name', orientation='h', title="Top 10 Repositórios (por estrelas)", color='stargazers_count')
st.plotly_chart(fig2, use_container_width=True)

# --- Gráfico: Atividade por ano ---
df['ano'] = df['created_at'].dt.year
year_count = df['ano'].value_counts().sort_index()
fig3 = px.line(x=year_count.index, y=year_count.values, labels={'x': 'Ano', 'y': 'Repositórios Criados'}, title="Atividade de criação por ano")
st.plotly_chart(fig3, use_container_width=True)
