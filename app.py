import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px

from openai import OpenAI

from auth.auth import require_login, logout_button
from auth.db import init_db

from ai.data_analyzer import analisar_dataframe, detectar_kpis
from ai.schema_detector import detectar_schema

from utils.file_reader import carregar_arquivo
from analytics.kpi_engine import mostrar_kpis
from dashboards.chart_builder import criar_graficos
from dashboards.auto_dashboard import gerar_dashboard_automatico


# ==============================
# CONFIG
# ==============================

st.set_page_config(
    page_title="📊 BI Inteligente – SaaS",
    layout="wide"
)

init_db()
require_login()

user = st.session_state.user

st.markdown(
f"""
### 📊 BI Inteligente  
Empresa: **{user['company_name']}**  
Usuário: **{user['name']}**
"""
)

logout_button()

st.divider()


# ==============================
# OPENAI
# ==============================

api_key = "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"

client = None

if api_key:
    client = OpenAI(api_key=api_key)
else:
    st.warning("⚠ OPENAI_API_KEY não configurada. IA desativada.")


# ==============================
# UPLOAD
# ==============================

arquivo = st.file_uploader(
    "📂 Envie um arquivo",
    type=["xlsx", "xls", "pdf"]
)

if not arquivo:
    st.stop()

try:
    dados = carregar_arquivo(arquivo)

except Exception as e:

    st.error("Erro ao carregar arquivo.")
    st.exception(e)
    st.stop()


# ==============================
# PROCESSAR DADOS
# ==============================

if isinstance(dados, pd.DataFrame):

    df = dados

else:

    xls = dados["xls"]

    st.subheader("📑 Abas disponíveis no arquivo")

    abas = st.multiselect(
        "Selecione as abas para análise",
        dados["abas"]
    )

    if not abas:
        st.info("Selecione pelo menos uma aba.")
        st.stop()

    modo = st.radio(
        "Modo de análise",
        [
            "Analisar abas separadamente",
            "Unir abas"
        ]
    )

    try:

        if modo == "Unir abas":

            lista_dfs = []

            for aba in abas:

                temp = pd.read_excel(xls, sheet_name=aba)

                temp.columns = temp.columns.astype(str).str.strip()

                temp["__aba__"] = aba

                lista_dfs.append(temp)

            df = pd.concat(lista_dfs, ignore_index=True)

        else:

            aba = st.selectbox(
                "Escolha a aba para análise",
                abas
            )

            df = pd.read_excel(xls, sheet_name=aba)

    except Exception as e:

        st.error("Erro ao ler Excel.")
        st.exception(e)
        st.stop()

    df.columns = df.columns.astype(str).str.strip()

    df = df.dropna(how="all")


# ==============================
# LIMPEZA INTELIGENTE (PDF / DADOS SUJOS)
# ==============================

df = df.dropna(axis=1, how="all")
df = df.dropna(how="all")
df = df.reset_index(drop=True)

# tentar detectar header correto
for i in range(min(5, len(df))):

    linha = df.iloc[i].astype(str)

    if linha.str.len().mean() > 3 and linha.nunique() > 3:

        df.columns = linha
        df = df[i+1:]
        break

# limpar colunas
df.columns = [str(c).strip() for c in df.columns]

# remover duplicadas
df = df.loc[:, ~df.columns.duplicated()]

# converter números automaticamente
for col in df.columns:

    df[col] = pd.to_numeric(df[col], errors="ignore")


if df.empty:

    st.warning("Arquivo sem dados.")
    st.stop()


# ==============================
# MOSTRAR DADOS
# ==============================

st.header("📋 Dados carregados")

st.dataframe(df, use_container_width=True)


# ==============================
# ANALISAR DADOS
# ==============================

estrutura = analisar_dataframe(df)

schema = detectar_schema(df)

kpis = detectar_kpis(df)


# ==============================
# KPIs
# ==============================

mostrar_kpis(kpis)


# ==============================
# DASHBOARD INTERATIVO
# ==============================

dashboard_info = criar_graficos(df, schema)


# ==============================
# DASHBOARD AUTOMÁTICO
# ==============================

auto_dashboard = gerar_dashboard_automatico(df, schema)


# ==============================
# IA INSIGHTS
# ==============================

st.header("🧠 Insights Inteligentes")

if client:

    if st.button("Gerar análise da IA"):

        try:

            contexto = {
                "empresa": user["company_name"],
                "registros": len(df),
                "colunas": list(df.columns),
                "schema": schema
            }

            prompt = f"""
Você é um analista de negócios.

Empresa: {contexto['empresa']}

Estrutura dos dados:
{json.dumps(contexto, ensure_ascii=False)}

Explique:

- O que os dados indicam
- Possíveis riscos
- Oportunidades
- Recomendações estratégicas
"""

            r = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Especialista em análise de negócios."},
                    {"role": "user", "content": prompt}
                ]
            )

            st.success("📢 Análise da IA")

            st.write(r.choices[0].message.content)

        except Exception as e:

            st.error("Erro ao gerar análise.")
            st.exception(e)


# ==============================
# CHAT COM IA
# ==============================

st.divider()

st.header("💬 Pergunte aos Dados")

pergunta = st.text_input(
    "Pergunte algo sobre os dados",
    placeholder="Ex: gráfico de vendas por cliente ou criar dashboard de vendas"
)

if pergunta and client:

    try:

        dados_contexto = df.head(200).astype(str).to_dict(orient="records")

        prompt = f"""
Você é um analista de BI.

Colunas disponíveis:
{list(df.columns)}

Dados de exemplo:
{json.dumps(dados_contexto, ensure_ascii=False)}

Pergunta do usuário:
{pergunta}

Responda SOMENTE em JSON.

TEXTO:
{{ "tipo":"texto","resposta":"..." }}

GRÁFICO:
{{ "tipo":"grafico","grafico":"bar|line|pie","x":"coluna","y":"coluna" }}

DASHBOARD:
{{ "tipo":"dashboard","graficos":[{{"grafico":"bar","x":"coluna","y":"coluna"}}] }}
"""

        r = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Especialista em BI"},
                {"role": "user", "content": prompt}
            ]
        )

        resposta = r.choices[0].message.content

        try:

            resp = json.loads(resposta)

            if resp["tipo"] == "texto":

                st.write(resp["resposta"])

            elif resp["tipo"] == "grafico":

                x = resp["x"]
                y = resp["y"]

                if x.isdigit():
                    x = df.columns[int(x)]

                if y.isdigit():
                    y = df.columns[int(y)]

                df[y] = pd.to_numeric(df[y], errors="coerce")

                if resp["grafico"] == "bar":
                    fig = px.bar(df, x=x, y=y)

                elif resp["grafico"] == "line":
                    fig = px.line(df, x=x, y=y)

                else:
                    fig = px.pie(df, names=x, values=y)

                st.plotly_chart(fig, use_container_width=True)

            elif resp["tipo"] == "dashboard":

                for g in resp["graficos"]:

                    x = g["x"]
                    y = g["y"]

                    if x.isdigit():
                        x = df.columns[int(x)]

                    if y.isdigit():
                        y = df.columns[int(y)]

                    df[y] = pd.to_numeric(df[y], errors="coerce")

                    if g["grafico"] == "bar":
                        fig = px.bar(df, x=x, y=y)

                    elif g["grafico"] == "line":
                        fig = px.line(df, x=x, y=y)

                    else:
                        fig = px.pie(df, names=x, values=y)

                    st.plotly_chart(fig, use_container_width=True)

        except:

            st.write(resposta)

    except Exception as e:

        st.error("Erro ao consultar IA.")

        st.exception(e)



