import pdfplumber
import pandas as pd
import re

def ler_pdf(file):

    texto = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

    linhas = texto.split("\n")

    dados = []

    for linha in linhas:

        padrao = r"(\d{3,4})\s+(.+?)\s+(\d+)\s+R\$\s*([\d,]+)\s+R\$\s*([- \d,]+)"

        match = re.search(padrao, linha)

        if match:
            codigo = match.group(1)
            nome = match.group(2)
            itens = int(match.group(3))
            vendas = float(match.group(4).replace(",", "."))
            lucro = float(match.group(5).replace(",", ".").replace(" ", ""))

            dados.append({
                "Código": codigo,
                "Cliente": nome,
                "Itens": itens,
                "Vendas": vendas,
                "Lucro": lucro
            })

    df = pd.DataFrame(dados)

    return df