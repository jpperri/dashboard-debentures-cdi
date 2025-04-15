import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Debêntures CDI+", layout="wide")

# --- Carregar dados ---
@st.cache_data
def load_data():
    return pd.read_excel("Deb CDI+.xlsx", engine="openpyxl")

df = load_data()

# --- Tratamento robusto ---
df["ANBIMA"] = pd.to_numeric(df.get("ANBIMA"), errors="coerce")
df["Duration"] = pd.to_numeric(df.get("Duration"), errors="coerce")
df["PU"] = pd.to_numeric(df.get("PU"), errors="coerce")
df["Spread_bps"] = df["ANBIMA"] * 10000
df["Setor"] = df.get("Setor", "Não informado").fillna("Não informado")

# --- Título ---
st.title("📊 Dashboard de Debêntures CDI+")

# --- Filtro por setor ---
setores = st.multiselect("Filtrar por Setor", options=df["Setor"].unique(), default=list(df["Setor"].unique()))
df = df[df["Setor"].isin(setores)]

# --- Pré-visualizar dados para debug (opcional, pode remover depois) ---
st.subheader("🔍 Amostra de dados usados no gráfico")
df_plot = df.dropna(subset=["Duration", "Spread_bps", "Setor"])
st.write(df_plot.head())

# --- Gráfico (com fallback) ---
st.subheader("📈 Scatter: Spread ANBIMA vs. Duration")
if df_plot.empty:
    st.warning("⚠️ Dados insuficientes para gerar o gráfico. Verifique os filtros e a planilha.")
else:
    try:
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
    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {e}")

# --- Tabela de dados filtrados ---
st.subheader("📋 Tabela de Debêntures")
st.dataframe(
    df[["Codigo", "Emissor", "Setor", "Duration", "Spread_bps", "PU", "Vencimento"]].dropna(how='all'),
    use_container_width=True
)
