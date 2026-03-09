import pandas as pd

def load_excel(file, abas):
    xls = pd.ExcelFile(file)

    df = pd.read_excel(xls, sheet_name=abas[0])
    df.columns = df.columns.astype(str).str.strip()
    df = df.dropna(how="all")

    if len(abas) == 2:
        df2 = pd.read_excel(xls, sheet_name=abas[1])
        df2.columns = df2.columns.astype(str).str.strip()
        df2 = df2.dropna(how="all")
        return df, df2

    return df, None