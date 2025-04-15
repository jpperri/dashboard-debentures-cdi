import plotly.graph_objects as go
import numpy as np
from scipy.optimize import curve_fit

# === MÉDIA DE SPREAD POR SETOR ===
st.markdown("## 🧮 Média de Spread por Setor")
spread_por_setor = df.groupby("Setor")["ANBIMA_pct"].mean().reset_index().sort_values("ANBIMA_pct", ascending=False)

col1, col2 = st.columns([1, 2])
with col1:
    st.dataframe(
        spread_por_setor.rename(columns={"ANBIMA_pct": "Spread Médio (%)"}),
        use_container_width=True
    )
with col2:
    fig_bar = px.bar(
        spread_por_setor,
        x="ANBIMA_pct",
        y="Setor",
        orientation="h",
        labels={"ANBIMA_pct": "Spread Médio (%)"},
        title="Spread Médio por Setor"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# === VISÃO DO EMISSOR ===
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

    # === CURVA TEÓRICA COM AJUSTE EXPONENCIAL ===
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
        fig_fit.add_trace(go.Scatter(
            x=durations,
            y=spreads,
            mode='markers+text',
            name='Títulos',
            text=df_emissor["Código"],
            textposition="top center"
        ))
        fig_fit.add_trace(go.Scatter(
            x=x_model,
            y=y_model,
            mode='lines',
            name='Curva Interpolada'
        ))
        fig_fit.update_layout(
            title=f"Curva Teórica Ajustada - {emissor_sel}",
            xaxis_title="Duration (anos)",
            yaxis_title="Spread (bps)",
            height=600
        )
        st.plotly_chart(fig_fit, use_container_width=True)
    except Exception as e:
        st.error(f"Não foi possível ajustar a curva: {e}")

