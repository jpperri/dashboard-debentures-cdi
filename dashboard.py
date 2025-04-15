import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Debêntures CDI+", layout="wide")

# --- Carregar dados ---
@st.cache_data
def load_data():
    return pd.read_excel("Deb CDI+.xlsx", engine="openpyxl")

df = load_data()

# --- Tratamento de dados ---
df['Spread_bps'] = pd.to_numeric(df.get('ANBIMA'), errors='coerce') * 10000
df['Duration'] = pd.to_numeric(df.get('Duration'), errors='coerce')
df['Setor'] = df.get('Setor').fillna("Não informado")
df['PU'] = pd.to_numeric(df.get('PU'), errors='coerce')

# --- Título ---
st.title("📊 Dashboard de Debêntures CDI+")

# --- Filtros ---
setores = st.multiselect(
    "Filtrar por Setor",
    options=df["Setor"].unique(),
    default=list(df["Setor"].unique())
)
df = df[df["Setor"].isin(setores)]

# --- Gráfico com validações ---
st.markdown("## 🎯 Spread vs Duration")

# Verifica se colunas necessárias existem e não estão vazias
if df[["Duration", "Spread_bps", "Setor"]].dropna().empty:
    st.warning("⚠️ Nenhum dado válido disponível para o gráfico.")
else:
    df_plot = df.dropna(subset=["Duration", "Spread_bps", "Setor"])
    fig = px.scatter(
        df_plot,
        x="Duration",
        y="Spread_bps",
        color="Setor",
        hover_data=["Codigo", "Emissor", "PU", "Vencimento"],
        title="Spread ANBIMA vs. Duration",
        labels={"Duration": "Duration (anos)", "Spread_bps": "Spread (bps)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Tabela final ---
st.markdown("## 📋 Tabela de Debêntures")
st.dataframe(
    df[["Codigo", "Emissor", "Setor", "Duration", "Spread_bps", "PU", "Vencimento"]].dropna(how='all'),
    use_container_width=True
)
