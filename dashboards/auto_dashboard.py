import streamlit as st
import pandas as pd


def gerar_dashboard_automatico(df, schema):

    st.header("🚀 Dashboard Automático")

    dimensoes = schema["dimensoes"]
    metricas = schema["metricas"]

    info = {}

    if not dimensoes or not metricas:
        st.warning("Não foi possível gerar dashboard automático.")
        return info

    # =========================
    # TOP CATEGORIAS
    # =========================

    dim = dimensoes[0]
    met = metricas[0]

    try:

        top = df.groupby(dim)[met].sum().sort_values(ascending=False).head(10)

        st.subheader(f"🏆 Top 10 {dim}")

        st.bar_chart(top)

        info["top"] = top.to_dict()

    except:
        pass

    # =========================
    # DISTRIBUIÇÃO
    # =========================

    try:

        st.subheader(f"📊 Distribuição de {met}")

        st.bar_chart(df[met].value_counts().head(20))

    except:
        pass

    # =========================
    # COMPARAÇÃO ENTRE MÉTRICAS
    # =========================

    if len(metricas) >= 2:

        m1 = metricas[0]
        m2 = metricas[1]

        try:

            st.subheader(f"📈 Comparação {m1} x {m2}")

            st.scatter_chart(df[[m1, m2]])

        except:
            pass

    # =========================
    # OUTLIERS
    # =========================

    try:

        media = df[met].mean()

        outliers = df[df[met] > media * 2]

        if not outliers.empty:

            st.subheader("⚠ Valores fora da curva")

            st.dataframe(outliers.head(10))

    except:
        pass

    return info