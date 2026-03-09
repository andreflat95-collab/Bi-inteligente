import streamlit as st


def criar_graficos(df, schema):

    st.header("📈 Dashboard Inteligente")

    dimensoes = schema["dimensoes"]
    metricas = schema["metricas"]

    if not dimensoes or not metricas:

        st.warning("Não foi possível gerar gráficos automaticamente.")

        return {}

    dim = st.selectbox("Dimensão (categoria)", dimensoes)

    met = st.selectbox("Métrica (valor)", metricas)

    try:

        top = df.groupby(dim)[met].sum().sort_values(ascending=False).head(10)

        st.subheader(f"🏆 Top 10 por {met}")

        st.bar_chart(top)

    except:

        st.warning("Não foi possível gerar gráfico.")

    return {
        "dimensao": dim,
        "metrica": met
    }