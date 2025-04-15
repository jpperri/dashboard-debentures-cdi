import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Debêntures CDI+", layout="wide")

# --- Carregar dados ---
@st.cache_data
def load_data():
    return pd.read_excel("Deb CDI+.xlsx", engine="openpyxl")

df = load_data()

# --- Tratamento ---
df['Spread_bps'] = pd.to_numeric(df['ANBIMA'], errors='coerce') * 10000
df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')
df['Setor'] = df['Setor'].fillna("Não informado")

# --- Título ---
st.title("📊 Dashboard de Debêntures CDI+")

# --- Filtros interativos ---
setores = st.multiselect(
    "Filtrar por Setor", 
    options=df["Setor"].unique(), 
    default=list(df["Setor"].unique())
)

df = df[df["Setor"].isin(setores)]

# --- Gráfico Scatter (com validação de dados) ---
df_plot = df.dropna(subset=["Duration", "Spread_bps", "Setor"])

if df_plot.empty:
    st.warning("⚠️ Nenhum dado disponível para os filtros atuais.")
else:
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

# --- Tabela com dados filtrados ---
st.markdown("### 📋 Tabela de Debêntures")
st.dataframe(
    df[["Codigo", "Emissor", "Setor", "Duration", "Spread_bps", "PU", "Vencimento"]],
    use_container_width=True
)
