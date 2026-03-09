import pandas as pd


def analisar_dataframe(df):

    estrutura = {
        "colunas": list(df.columns),
        "registros": len(df)
    }

    return estrutura


def detectar_kpis(df):

    kpis = {}

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):

            kpis[col] = df[col].sum()

    kpis["registros"] = len(df)

    return kpis