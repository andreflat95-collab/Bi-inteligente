import pandas as pd
import pdfplumber
import camelot
import tempfile
import re


# ======================================
# LIMPAR DATAFRAME
# ======================================

def limpar_dataframe(df):

    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")
    df = df.reset_index(drop=True)

    # tentar encontrar header real
    for i in range(min(10, len(df))):

        linha = df.iloc[i].astype(str)

        if linha.str.len().mean() > 2 and linha.nunique() > 2:

            df.columns = linha
            df = df[i+1:]
            break

    df.columns = [str(c).strip() for c in df.columns]

    # evitar colunas duplicadas
    cols = []

    for i, c in enumerate(df.columns):

        if c in cols:
            c = f"{c}_{i}"

        cols.append(c)

    df.columns = cols

    return df


# ======================================
# PARSER RELATORIO DE PRODUTOS
# ======================================

def extrair_relatorio_produtos(caminho):

    registros = []

    with pdfplumber.open(caminho) as pdf:

        for page in pdf.pages:

            texto = page.extract_text()

            if not texto:
                continue

            linhas = texto.split("\n")

            # DEBUG
            print("\n========== DEBUG PDF ==========")
            print("Primeiras linhas da página:")
            for l in linhas[:20]:
                print(l)
            print("================================\n")

            for linha in linhas:

                linha = linha.strip()

                # ignorar cabeçalhos comuns
                if (
                    "Página" in linha
                    or "DATA DA CONSULTA" in linha
                    or "MINISTÉRIO" in linha
                    or "Cód." in linha
                ):
                    continue

                # linha deve começar com código
                if not re.match(r'^\d{2,}', linha):
                    continue

                match = re.match(
                    r'^(\d+)\s+(.*?)\s+(\d+)\s+(\d+)\s+R?\$?\s*([\d.,]+)\s+(-?R?\$?\s*[\d.,]+)',
                    linha
                )

                if match:

                    registros.append({
                        "codigo": match.group(1),
                        "descricao": match.group(2),
                        "quantidade": match.group(3),
                        "numero_vendas": match.group(4),
                        "total_vendas": match.group(5),
                        "lucro": match.group(6)
                    })

    if not registros:
        return None

    return pd.DataFrame(registros)


# ======================================
# PARSER TEXTO GENERICO
# ======================================

def extrair_tabela_texto(caminho):

    linhas_validas = []

    with pdfplumber.open(caminho) as pdf:

        for page in pdf.pages:

            texto = page.extract_text()

            if not texto:
                continue

            linhas = texto.split("\n")

            for linha in linhas:

                if (
                    "|" in linha
                    or ";" in linha
                    or "\t" in linha
                    or re.search(r"\s{3,}", linha)
                ):

                    partes = re.split(r"\||;|\t|\s{3,}", linha)

                    partes = [p.strip() for p in partes if p.strip()]

                    if len(partes) > 1:
                        linhas_validas.append(partes)

    if not linhas_validas:
        return None

    max_cols = max(len(l) for l in linhas_validas)

    normalizado = []

    for linha in linhas_validas:

        while len(linha) < max_cols:
            linha.append(None)

        normalizado.append(linha)

    return pd.DataFrame(normalizado)


# ======================================
# CARREGAR PDF
# ======================================

def carregar_pdf(arquivo):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

        tmp.write(arquivo.read())
        caminho = tmp.name

    # ==============================
    # 1️⃣ TENTAR CAMELOT
    # ==============================

    print("Tentando Camelot...")

    try:

        tables = camelot.read_pdf(
            caminho,
            pages="all",
            flavor="lattice"
        )

        if tables:

            dfs = [t.df for t in tables if len(t.df.columns) > 1]

            if dfs:

                print("✔ Camelot conseguiu extrair tabela")

                df = pd.concat(dfs, ignore_index=True)

                return limpar_dataframe(df)

    except Exception as e:
        print("Camelot falhou:", e)

    # ==============================
    # 2️⃣ TENTAR PDFPLUMBER
    # ==============================

    print("Tentando pdfplumber...")

    try:

        tabelas = []

        with pdfplumber.open(caminho) as pdf:

            for page in pdf.pages:

                tables = page.extract_tables()

                if tables:

                    for table in tables:

                        df = pd.DataFrame(table)

                        tabelas.append(df)

        if tabelas:

            print("✔ pdfplumber encontrou tabelas")

            df = pd.concat(tabelas, ignore_index=True)

            return limpar_dataframe(df)

    except Exception as e:
        print("pdfplumber falhou:", e)

    # ==============================
    # 3️⃣ RELATORIO PRODUTOS
    # ==============================

    print("Tentando parser de relatório...")

    try:

        df = extrair_relatorio_produtos(caminho)

        if df is not None:

            print("✔ Parser de relatório funcionou")

            return limpar_dataframe(df)

    except Exception as e:
        print("Parser relatório falhou:", e)

    # ==============================
    # 4️⃣ FALLBACK TEXTO
    # ==============================

    print("Tentando fallback texto...")

    try:

        df = extrair_tabela_texto(caminho)

        if df is not None:

            print("✔ Fallback texto funcionou")

            return limpar_dataframe(df)

    except Exception as e:
        print("Fallback falhou:", e)

    raise Exception("Não foi possível extrair dados do PDF.")


# ======================================
# CARREGAR ARQUIVO
# ======================================

def carregar_arquivo(arquivo):

    nome = arquivo.name.lower()

    # ==============================
    # EXCEL
    # ==============================

    if nome.endswith(".xlsx") or nome.endswith(".xls"):

        xls = pd.ExcelFile(arquivo)

        return {
            "xls": xls,
            "abas": xls.sheet_names
        }

    # ==============================
    # PDF
    # ==============================

    if nome.endswith(".pdf"):

        df = carregar_pdf(arquivo)

        return df

    raise Exception("Formato não suportado.")