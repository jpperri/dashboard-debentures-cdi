import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Debêntures CDI+", layout="wide")

# Carregar Excel local do repositório
@st.cache_data
def load_data():
    df = pd.read_excel("Deb CDI+.xlsx", engine="openpyxl")
    df["Spread_bps"] = pd.to_numeric(df["ANBIMA"], errors="coerce") * 10000
    df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce")
    df["PU"] = pd.to_numeric(df["PU"], errors="coerce")
    df["Setor"] = df["Setor"].fillna("Não informado")
    df["Vencimento"] = pd.to_datetime(df["Vencimento"], errors="coerce")
    df["Ano_Venc"] = df["Vencimento"].dt.year
    return df

df = load_data()

# Título
st.title("📊 Dashboard Interativo — Debêntures CDI+")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Debêntures", len(df))
col2.metric("📈 Spread Médio", f"{df['Spread_bps'].mean():.1f} bps")
col3.metric("⏳ Duration Média", f"{df['Duration'].mean():.2f} anos")
col4.metric("📅 Último Vencimento", df["Vencimento"].max().strftime("%d/%m/%Y") if pd.notnull(df["Vencimento"].max()) else "-")

st.markdown("---")

# Filtros
setores = st.multiselect("Filtrar por Setor", options=df["Setor"].unique(), default=list(df["Setor"].unique()))
anos_venc = st.multiselect("Filtrar por Ano de Vencimento", options=sorted(df["Ano_Venc"].dropna().unique()), default=sorted(df["Ano_Venc"].dropna().unique()))
df_filt = df[df["Setor"].isin(setores) & df["Ano_Venc"].isin(anos_venc)]

# Gráfico Scatter
st.subheader("📈 Spread ANBIMA (bps) vs Duration")
df_plot = df_filt.dropna(subset=["Duration", "Spread_bps", "Setor"])

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

# Rankings
st.subheader("🏆 Top 10 maiores spreads")
st.dataframe(df_filt.sort_values("Spread_bps", ascending=False).head(10))

st.subheader("📉 Top 10 menores spreads")
st.dataframe(df_filt.sort_values("Spread_bps", ascending=True).head(10))

# Concentração por emissor
st.subheader("🏢 Top 5 Emissores por Número de Debêntures")
top_emissores = df_filt["Emissor"].value_counts().head(5)
st.bar_chart(top_emissores)

# Tabela e download
st.subheader("📋 Tabela de Debêntures Filtradas")
st.dataframe(df_filt[["Código", "Emissor", "Setor", "Duration", "Spread_bps", "PU", "Vencimento"]], use_container_width=True)

csv = df_filt.to_csv(index=False).encode('utf-8')
st.download_button("📥 Baixar CSV com dados filtrados", data=csv, file_name="debentures_filtradas.csv", mime='text/csv')
