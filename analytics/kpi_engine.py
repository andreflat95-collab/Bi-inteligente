import streamlit as st


def mostrar_kpis(kpis):

    st.header("📊 KPIs Detectados")

    cols = st.columns(4)

    i = 0

    for nome, valor in kpis.items():

        if nome == "registros":
            continue

        with cols[i % 4]:

            try:
                st.metric(nome, f"{valor:,.2f}")
            except:
                st.metric(nome, valor)

        i += 1