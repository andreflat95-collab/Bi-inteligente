import json
import streamlit as st
from ai.client import get_client

def analyze_dashboard(df_f, dashboard_info):
    st.header("🧠 Insights Inteligentes")

    if not st.button("Analisar Dashboard com IA"):
        return

    contexto = {
        "registros": len(df_f),
        "blocos": dashboard_info
    }

    prompt = f"""
Você é um analista de dados para gestores.

Com base nesse dashboard:
{json.dumps(contexto)}

Explique:
- O que está acontecendo nos dados
- Riscos
- Oportunidades
- Decisões práticas
"""

    try:
        client = get_client()

        r = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um analista de negócios."},
                {"role": "user", "content": prompt}
            ]
        )

        st.success("📢 Insights da IA")
        st.write(r.choices[0].message.content)

    except Exception as e:
        st.error("Erro ao chamar IA")
        st.exception(e)