import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Debêntures CDI+", layout="wide")

# --- Google Sheets (exportado como CSV) ---
sheet_id = "1l9ki6Vv0ucrEcL-VvDR61a6o8xY8D8CA"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

# --- Carregar dados ---
@st.cache_data
def load_data():
    df = pd.read_csv(sheet_url)
    df["Spread_bps"] = pd.to_numeric(df["ANBIMA"], errors="coerce") * 10000
    df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce")
    df["PU"] = pd.to_numeric(df["PU"], errors="coerce")
    df["Setor"] = df["Setor"].fillna("Não informado")
    return df

df = load_data()

# --- Título ---
st.title("📊 Dashboard Interativo — Debêntures CDI+")

# --- Filtros ---
setores = st.multiselect("Filtrar por Setor", options=df["Setor"].unique(), default=list(df["Setor"].unique()))
df_filt = df[df["Setor"].isin(setores)]

# --- Gráfico ---
df_plot = df_filt.dropna(subset=["Duration", "Spread_bps", "Setor"])
st.subheader("📈 Spread ANBIMA (bps) vs Duration")

if df_plot.empty:
    st.warning("⚠️ Nenhum dado disponível para o gráfico com os filtros atuais.")
else:
    fig = px.scatter(
        df_plot,
        x="Duration",
        y="Spread_bps",
        color="Setor",
        hover_data=["Código", "Emissor", "PU", "Vencimento"],
        title="Spread ANBIMA vs Duration",
        labels={"Duration": "Duration (anos)", "Spread_bps": "Spread (bps)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Tabela ---
st.subheader("📋 Tabela de Debêntures")
st.dataframe(
    df_filt[["Código", "Emissor", "Setor", "Duration", "Spread_bps", "PU", "Vencimento"]],
    use_container_width=True
)

