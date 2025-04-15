import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.optimize import curve_fit
from PIL import Image
import io
import base64

st.set_page_config(page_title="REAG Crédito - Monitor de Debêntures CDI+", layout="wide")

# === Cabeçalho visual com redimensionamento ===
image = Image.open("logopage.png")
resized_image = image.resize((image.width // 2, image.height // 2))
st.image(resized_image, use_container_width=True)

# === Carregamento de dados ===
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
is_dark = st.get_option("theme.base") == "dark"
interpol_color = "white" if is_dark else "black"

st.title("📊 REAG Crédito - Monitor de Debêntures CDI+")

from fpdf import FPDF

tab1, tab2, tab3, tab4 = st.tabs(["📈 Visão Geral", "🏦 Emissores", "🏭 Setorial", "📄 Relatório Executivo"])

# === Funções utilitárias ===
def preparar_tabela(df_input):
    df_show = df_input.copy()
    df_show["Vencimento"] = df_show["Vencimento"].dt.strftime("%d/%m/%Y")
    df_show["BID"] = df_show["BID_pct"].map("{:.2f}%".format)
    df_show["OFFER"] = df_show["OFFER_pct"].map("{:.2f}%".format)
    df_show["ANBIMA"] = df_show["ANBIMA_pct"].map("{:.2f}%".format)
    return df_show[["Código", "Emissor", "Setor", "Duration", "BID", "OFFER", "ANBIMA", "PU", "Vencimento"]]

# === VISÃO GERAL ===
# === VISÃO GERAL ===
with tab1:
    st.header("📈 Visão Geral")

    # Estatísticas principais
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📄 Total Debêntures", len(df))
    col2.metric("📈 Spread Médio (bps)", f"{df['Spread_bps'].mean():.1f}")
    col3.metric("⏳ Duration Média (anos)", f"{df['Duration'].mean():.2f}")
    col4.metric("📅 Último Vencimento", df["Vencimento"].max().strftime("%d/%m/%Y"))

    # Top 3 maiores e menores spreads
    st.subheader("🏅 Destaques de Spread")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔝 Top 3 Maiores Spreads")
        st.dataframe(preparar_tabela(df.sort_values("Spread_bps", ascending=False).head(3)), use_container_width=True)
    with col2:
        st.markdown("### 🔻 Top 3 Menores Spreads")
        st.dataframe(preparar_tabela(df.sort_values("Spread_bps", ascending=True).head(3)), use_container_width=True)

    # Filtros
    st.subheader("🎛 Filtros")
    setores_filtro = st.multiselect("Setor", sorted(df["Setor"].dropna().unique()), default=[])
    anos_filtro = st.multiselect("Ano de Vencimento", sorted(df["Ano_Venc"].dropna().unique()), default=[])

    df_filt = df.copy()
    if setores_filtro:
        df_filt = df_filt[df_filt["Setor"].isin(setores_filtro)]
    if anos_filtro:
        df_filt = df_filt[df_filt["Ano_Venc"].isin(anos_filtro)]

    # Gráfico
    st.subheader("📈 Spread ANBIMA (bps) vs Duration")
    df_plot = df_filt.dropna(subset=["Duration", "Spread_bps", "Setor"])
    fig = px.scatter(
        df_plot,
        x="Duration",
        y="Spread_bps",
        color="Setor",
        hover_data=["Código", "Emissor", "PU", "Vencimento"],
        height=800,
        labels={"Duration": "Duration (anos)", "Spread_bps": "Spread (bps)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top 10 tabelas
    st.subheader("📊 Top 10 Maiores Spreads")
    st.dataframe(preparar_tabela(df_filt.sort_values("Spread_bps", ascending=False).head(10)), use_container_width=True)

    st.subheader("📉 Top 10 Menores Spreads")
    st.dataframe(preparar_tabela(df_filt.sort_values("Spread_bps", ascending=True).head(10)), use_container_width=True)

    # Tabela final
    st.subheader("📋 Tabela Completa de Debêntures")
    st.dataframe(preparar_tabela(df_filt.sort_values("Vencimento")), use_container_width=True)


# === EMISSORES ===
with tab2:
    st.header("🏦 Curva por Emissor")

    emissores = sorted(df["Emissor"].dropna().unique())
    localiza_index = next((i for i, e in enumerate(emissores) if "Localiza Rent a Car" in e), 0)
    emissor_sel = st.selectbox("Selecione o emissor", emissores, index=localiza_index)

    df_emissor = df[df["Emissor"] == emissor_sel].dropna(subset=["Duration", "Spread_bps"]).sort_values("Duration")

    fig_emissor = go.Figure()
    symbols = ['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
               'star', 'hexagram', 'hourglass', 'bowtie', 'pentagon']
    for i, (index, row) in enumerate(df_emissor.iterrows()):
        fig_emissor.add_trace(go.Scatter(
            x=[row["Duration"]],
            y=[row["Spread_bps"]],
            mode="markers+text",
            marker_symbol=symbols[i % len(symbols)],
            marker=dict(size=12),
            text=[row["Código"]],
            name=row["Código"],
            textposition="top center"
        ))

    def curva_exp(x, a, b, c):
        return a * np.exp(-b * x) + c

    try:
        durations = df_emissor["Duration"].values
        spreads = df_emissor["Spread_bps"].values
        popt, _ = curve_fit(curva_exp, durations, spreads, maxfev=10000)
        x_model = np.linspace(min(durations), max(durations), 100)
        y_model = curva_exp(x_model, *popt)
        fig_emissor.add_trace(go.Scatter(
            x=x_model,
            y=y_model,
            mode="lines",
            name="Curva Interpolada",
            line=dict(color=interpol_color, dash='dash')
        ))
    except Exception:
        st.info("⚠️ Curva não ajustada — dados insuficientes.")

    fig_emissor.update_layout(
        title=f"Curva do Emissor: {emissor_sel}",
        xaxis_title="Duration (anos)",
        yaxis_title="Spread (bps)",
        height=600
    )
    st.plotly_chart(fig_emissor, use_container_width=True)

# === SETORIAL ===
with tab3:
    st.header("🏭 Média de Spread por Setor")

    spread_por_setor = (
        df.groupby("Setor")["ANBIMA_pct"]
        .mean()
        .reset_index()
        .sort_values("ANBIMA_pct", ascending=False)
    )

    fig_bar = px.bar(
        spread_por_setor,
        x="ANBIMA_pct",
        y="Setor",
        orientation="h",
        labels={"ANBIMA_pct": "Spread Médio (%)"},
        title="Spread Médio por Setor",
        height=800
    )
    st.plotly_chart(fig_bar, use_container_width=True)
from fpdf import FPDF

# ABA: RELATÓRIO EXECUTIVO
with tab4:
    st.header("📄 Relatório Executivo - Visão Geral")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "REAG Crédito - Monitor de Debêntures CDI+", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)

    # Estatísticas
    pdf.cell(0, 10, f"Total de Debêntures: {len(df)}", ln=True)
    pdf.cell(0, 10, f"Spread Médio: {df['Spread_bps'].mean():.1f} bps", ln=True)
    pdf.cell(0, 10, f"Duration Média: {df['Duration'].mean():.2f} anos", ln=True)
    pdf.cell(0, 10, f"Último Vencimento: {df['Vencimento'].max().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

    # Top 3
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Top 3 Maiores Spreads", ln=True)
    pdf.set_font("Arial", "", 12)
    top3_maiores = df.sort_values("Spread_bps", ascending=False).head(3)
    for _, row in top3_maiores.iterrows():
        pdf.cell(0, 10, f"{row['Código']} - {row['Emissor']} - {row['Spread_bps']:.0f} bps", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Top 3 Menores Spreads", ln=True)
    pdf.set_font("Arial", "", 12)
    top3_menores = df.sort_values("Spread_bps", ascending=True).head(3)
    for _, row in top3_menores.iterrows():
        pdf.cell(0, 10, f"{row['Código']} - {row['Emissor']} - {row['Spread_bps']:.0f} bps", ln=True)

    # Geração como string e encode para bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')

    st.download_button(
        label="📥 Baixar Relatório PDF",
        data=pdf_bytes,
        file_name="Relatorio_Executivo_REAG.pdf",
        mime="application/pdf"
    )
