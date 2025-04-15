import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Debêntures CDI+", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("Deb CDI+.xlsx", engine="openpyxl")
    df["Spread_bps"] = pd.to_numeric(df["ANBIMA"], errors="coerce") * 10000
    df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce")
    df["PU"] = pd.to_numeric(df["PU"], errors="coerce")
    df["BID_pct"] = df["BID"] * 100
    df["OFFER_pct"] = df["OFFER"] * 100
    df["ANBIMA_pct"] = df["ANBIMA"] * 100
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

# Filtros com reset
st.subheader("🎛 Filtros")

col1, col2, col3 = st.columns([3, 3, 1])

with col1:
    setores_unicos = sorted(df["Setor"].dropna().unique())
    setores_filtro = st.multiselect("Setor", options=setores_unicos, default=[])
with col2:
    anos_venc = sorted(df["Ano_Venc"].dropna().unique())
    anos_filtro = st.multiselect("Ano de Vencimento", options=anos_venc, default=[])

with col3:
    if st.button("🔄 Resetar filtros"):
        setores_filtro = []
        anos_filtro = []

# Aplicar filtros
df_filt = df.copy()
if setores_filtro:
    df_filt = df_filt[df_filt["Setor"].isin(setores_filtro)]
if anos_filtro:
    df_filt = df_filt[df_filt["Ano_Venc"].isin(anos_filtro)]

# Gráfico
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

# Top 10 maiores e menores spreads
st.subheader("🏆 Top 10 maiores spreads")
top_maiores = df_filt.sort_values("Spread_bps", ascending=False).head(10)
top_maiores["Vencimento"] = top_maiores["Vencimento"].dt.strftime("%d/%m/%Y")
top_maiores["BID"] = top_maiores["BID_pct"].map("{:.2f}%".format)
top_maiores["OFFER"] = top_maiores["OFFER_pct"].map("{:.2f}%".format)
top_maiores["ANBIMA"] = top_maiores["ANBIMA_pct"].map("{:.2f}%".format)
st.dataframe(top_maiores[["Código", "Emissor", "Setor", "Duration", "Spread_bps", "BID", "OFFER", "ANBIMA", "PU", "Vencimento"]])

st.subheader("📉 Top 10 menores spreads")
top_menores = df_filt.sort_values("Spread_bps", ascending=True).head(10)
top_menores["Vencimento"] = top_menores["Vencimento"].dt.strftime("%d/%m/%Y")
top_menores["BID"] = top_menores["BID_pct"].map("{:.2f}%".format)
top_menores["OFFER"] = top_menores["OFFER_pct"].map("{:.2f}%".format)
top_menores["ANBIMA"] = top_menores["ANBIMA_pct"].map("{:.2f}%".format)
st.dataframe(top_menores[["Código", "Emissor", "Setor", "Duration", "Spread_bps", "BID", "OFFER", "ANBIMA", "PU", "Vencimento"]])

# Concentração por emissor
st.subheader("🏢 Top 5 Emissores por Quantidade")
top_emissores = df_filt["Emissor"].value_counts().head(5)
st.bar_chart(top_emissores)

# Tabela final com download
st.subheader("📋 Tabela de Debêntures Filtradas")
df_filt_display = df_filt.copy()
df_filt_display["Vencimento"] = df_filt_display["Vencimento"].dt.strftime("%d/%m/%Y")
df_filt_display["BID"] = df_filt_display["BID_pct"].map("{:.2f}%".format)
df_filt_display["OFFER"] = df_filt_display["OFFER_pct"].map("{:.2f}%".format)
df_filt_display["ANBIMA"] = df_filt_display["ANBIMA_pct"].map("{:.2f}%".format)

st.dataframe(
    df_filt_display[["Código", "Emissor", "Setor", "Duration", "Spread_bps", "BID", "OFFER", "ANBIMA", "PU", "Vencimento"]],
    use_container_width=True
)

csv = df_filt.to_csv(index=False).encode('utf-8')
st.download_button("📥 Baixar CSV com dados filtrados", data=csv, file_name="debentures_filtradas.csv", mime='text/csv')
