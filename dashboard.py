import pandas as pd
import streamlit as st
import plotly.express as px

# Carregando dados
df = pd.read_excel("Deb CDI+.xlsx")

# Tratamento
df['Spread_bps'] = df['ANBIMA'] * 10000
df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')

st.title("📈 Dashboard de Debêntures CDI+")

# Filtros
setores = st.multiselect("Filtrar por Setor", df["Setor"].unique(), default=list(df["Setor"].unique()))
df = df[df["Setor"].isin(setores)]

# Filtrar dados válidos antes do gráfico
df_validos = df.dropna(subset=["Duration", "Spread_bps"])

fig = px.scatter(
    df_validos,
    x="Duration",
    y="Spread_bps",
    color="Setor",
    hover_data=["Codigo", "Emissor", "PU", "Vencimento"],
    title="Spread ANBIMA vs. Duration"
)
st.plotly_chart(fig)

if df_validos.empty:
    st.warning("⚠️ Nenhum dado disponível para os filtros selecionados.")
else:
    fig = px.scatter(...)
    st.plotly_chart(fig)


# Gráfico principal
fig = px.scatter(
    df, x="Duration", y="Spread_bps", color="Setor",
    hover_data=["Codigo", "Emissor", "PU", "Vencimento"],
    title="Spread ANBIMA vs. Duration"
)
st.plotly_chart(fig)

# Tabela
st.markdown("### 🔎 Tabela de Debêntures")
st.dataframe(df)
