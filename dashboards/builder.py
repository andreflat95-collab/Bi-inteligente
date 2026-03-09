import streamlit as st
import plotly.express as px

def build_dashboard(df_f):
    st.header("🧱 Dashboard")

    num_blocos = st.slider("Quantidade de blocos", 1, 4, 1)
    dashboard_info = []

    for i in range(num_blocos):
        st.subheader(f"📦 Bloco {i+1}")

        tipo = st.selectbox(
            f"Tipo de gráfico {i+1}",
            ["Barra", "Linha"],
            key=f"tipo_{i}"
        )

        dimensao = st.selectbox(
            f"Dimensão (X) {i+1}",
            df_f.columns,
            key=f"x_{i}"
        )

        numericas = df_f.select_dtypes(include="number").columns.tolist()
        if not numericas:
            st.warning("Sem colunas numéricas")
            continue

        valor = st.selectbox(
            f"Métrica (Y) {i+1}",
            numericas,
            key=f"y_{i}"
        )

        try:
            fig = (
                px.bar(df_f, x=dimensao, y=valor)
                if tipo == "Barra"
                else px.line(df_f, x=dimensao, y=valor)
            )

            st.plotly_chart(fig, use_container_width=True)

            dashboard_info.append({
                "tipo": tipo,
                "dimensao": dimensao,
                "valor": valor
            })

        except:
            st.info("Combinação inválida")

    return dashboard_infoS