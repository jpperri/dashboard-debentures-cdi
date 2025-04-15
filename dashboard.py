import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.optimize import curve_fit

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

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Debêntures", len(df))
col2.metric("📈 Spread Médio", f"{df['Spread_bps'].mean():.1f} bps")
col3.metric("⏳ Duration Média", f"{df['Duration'].mean():.2f} anos")
col4.metric("📅 Último Vencimento", df["Vencimento"].max().strftime("%d/%m/%Y") if pd.notnull(df["Vencimento"].max()) else "-")

st.markdown("---")

# --- Filtros ---
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

df_filt = df.copy()
if setores_filtro:
    df_filt = df_filt[df_filt["Setor"].isin(setores_filtro)]
if anos_filtro:
    df_filt = df_filt[df_filt["Ano_Venc"].isin(anos_filtro)]

# --- Gráfico principal ---
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
        labels={"Duration": "Duration (anos)", "Spread_bps": "Spread (bps)"},
        height=800
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Função para formatar tabelas ---
def preparar_tabela(df_input):
    df_show = df_input.copy()
    df_show["Vencimento"] = df_show["Vencimento"].dt.strftime("%d/%m/%Y")
    df_show["BID"] = df_show["BID_pct"].map("{:.2f}%".format)
    df_show["OFFER"] = df_show["OFFER_pct"].map("{:.2f}%".format)
    df_show["ANBIMA"] = df_show["ANBIMA_pct"].map("{:.2f}%".format)
    return df_show[["Código", "Emissor", "Setor", "Duration", "BID", "OFFER", "ANBIMA", "PU", "Vencimento"]]

# --- Tabelas principais ---
st.subheader("🏆 Top 10 maiores spreads")
top_maiores = df_filt.sort_values("ANBIMA_pct", ascending=False).head(10)
st.dataframe(preparar_tabela(top_maiores), use_container_width=True)

st.subheader("📉 Top 10 menores spreads")
top_menores = df_filt.sort_values("ANBIMA_pct", ascending=True).head(10)
st.dataframe(preparar_tabela(top_menores), use_container_width=True)

st.subheader("📋 Tabela de Debêntures Filtradas")
df_filt_ord = df_filt.sort_values("Vencimento")
st.dataframe(preparar_tabela(df_filt_ord), use_container_width=True)

# --- Download ---
csv = df_filt.to_csv(index=False).encode('utf-8')
st.download_button("📥 Baixar CSV com dados filtrados", data=csv, file_name="debentures_filtradas.csv", mime='text/csv')

# --- Média de Spread por Setor ---
st.markdown("## 🧮 Média de Spread por Setor")
spread_por_setor = df.groupby("Setor")["ANBIMA_pct"].mean().reset_index().sort_values("ANBIMA_pct", ascending=False)

col1, col2 = st.columns([1, 2])
with col1:
    st.dataframe(spread_por_setor.rename(columns={"ANBIMA_pct": "Spread Médio (%)"}), use_container_width=True)
with col2:
    fig_bar = px.bar(spread_por_setor, x="ANBIMA_pct", y="Setor", orientation="h",
                     labels={"ANBIMA_pct": "Spread Médio (%)"}, title="Spread Médio por Setor")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Visão por Emissor ---
st.markdown("## 🏦 Títulos do Emissor por Vencimento")
emissor_sel = st.selectbox("🔎 Selecione um Emissor", sorted(df["Emissor"].dropna().unique()))
df_emissor = df[df["Emissor"] == emissor_sel].dropna(subset=["Duration", "Spread_bps", "Vencimento"])

if df_emissor.empty:
    st.warning("Este emissor não possui dados suficientes para visualização.")
else:
    df_emissor = df_emissor.sort_values("Vencimento")
    fig_curve = px.scatter(
        df_emissor,
        x="Vencimento",
        y="Spread_bps",
        text="Código",
        title=f"Títulos do Emissor: {emissor_sel}",
        labels={"Spread_bps": "Spread (bps)", "Vencimento": "Vencimento"},
        height=500
    )
    fig_curve.update_traces(mode="markers+text", textposition="top center")
    st.plotly_chart(fig_curve, use_container_width=True)

    # --- Curva Interpolada ---
    st.markdown("## 📈 Curva Teórica Interpolada do Emissor")

    def curva_exp(x, a, b, c):
        return a * np.exp(-b * x) + c

    try:
        durations = df_emissor["Duration"].values
        spreads = df_emissor["Spread_bps"].values
        popt, _ = curve_fit(curva_exp, durations, spreads, maxfev=5000)

        x_model = np.linspace(min(durations), max(durations), 100)
        y_model = curva_exp(x_model, *popt)

        fig_fit = go.Figure()
        fig_fit.add_trace(go.Scatter(x=durations, y=spreads, mode='markers+text',
                                     name='Títulos', text=df_emissor["Código"], textposition="top center"))
        fig_fit.add_trace(go.Scatter(x=x_model, y=y_model, mode='lines', name='Curva Interpolada'))
        fig_fit.update_layout(title=f"Curva Ajustada - {emissor_sel}",
                              xaxis_title="Duration (anos)", yaxis_title="Spread (bps)", height=600)
        st.plotly_chart(fig_fit, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao ajustar curva: {e}")
