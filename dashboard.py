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
    df["Vencimento"] = pd.to_datetime(df["Vencimento"], dayfirst=True, errors="coerce")
    df["Ano_Venc"] = df["Vencimento"].dt.year
    return df

df = load_data()

st.title("📊 Dashboard Interativo — Debêntures CDI+")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Debêntures", len(df))
col2.metric("📈 Spread Médio", f"{df['Spread_bps'].mean():.1f} bps")
col3.metric("⏳ Duration Média", f"{df['Duration'].mean():.2f} anos")
col4.metric("📅 Último Vencimento", df["Vencimento"].max().strftime("%d/%m/%Y") if pd.notnull(df["Vencimento"].max()) else "-")

st.markdown("---")

# Filtros
st.subheader("🎛 Filtros")
col1, col2, col3 = st.columns([3, 3, 1])

with col1:
    setores_filtro = st.multiselect("Setor", options=sorted(df["Setor"].dropna().unique()), default=[])

with col2:
    anos_filtro = st.multiselect("Ano de Vencimento", options=sorted(df["Ano_Venc"].dropna().unique()), default=[])

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

# Tabelas - Top 10 maiores e menores spreads
def preparar_tabela(df_input):
    df_show = df_input.copy()
    df_show["Vencimento"] = df_show["Vencimento"].dt.strftime("%d/%m/%Y")
    df_show["BID"] = df_show["BID_pct"].map("{:.2f}%".format)
    df_show["OFFER"] = df_show["OFFER_pct"].map("{:.2f}%".format)
    df_show["ANBIMA"] = df_show["ANBIMA_pct"].map("{:.2f}%".format)
    return df_show[["Código", "Emissor", "Setor", "Duration", "BID", "OFFER", "ANBIMA", "PU", "Vencimento"]]

st.subheader("🏆 Top 10 maiores spreads")
top_maiores = df_filt.sort_values("ANBIMA_pct", ascending=False).head(10)
st.data_editor(preparar_tabela(top_maiores), use_container_width=True, hide_index=True, column_config={
    "Emissor": st.column_config.TextColumn(width="medium")
})

st.subheader("📉 Top 10 menores spreads")
top_menores = df_filt.sort_values("ANBIMA_pct", ascending=True).head(10)
st.data_editor(preparar_tabela(top_menores), use_container_width=True, hide_index=True, column_config={
    "Emissor": st.column_config.TextColumn(width="medium")
})

# Tabela final + download
st.subheader("📋 Tabela de Debêntures Filtradas")
st.data_editor(preparar_tabela(df_filt), use_container_width=True, hide_index=True, column_config={
    "Emissor": st.column_config.TextColumn(width="medium")
})

csv = df_filt.to_csv(index=False).encode('utf-8')
st.download_button("📥 Baixar CSV com dados filtrados", data=csv, file_name="debentures_filtradas.csv", mime='text/csv')
