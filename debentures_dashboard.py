# debentures_dashboard.py
import pandas as pd
import streamlit as st
import plotly.express as px

# Carregar os dados (do Excel atualizado ou API)
df = pd.read_excel("Deb CDI+.xlsx")

# Tratamento de dados
df['Spread_bps'] = df['ANBIMA'] * 10000
df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')

# Título
st.title("Dashboard Interativo - Debêntures CDI+")

# Filtros
setores = st.multiselect("Setor", df["Setor"].unique(), default=list(df["Setor"].unique()))
df_filtered = df[df["Setor"].isin(setores)]

# Gráfico
fig = px.scatter(df_filtered, x="Duration", y="Spread_bps", color="Setor", hover_data=["Emissor", "Código"])
st.plotly_chart(fig)
