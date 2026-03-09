import pandas as pd


def detectar_schema(df):

    schema = {
        "dimensoes": [],
        "metricas": []
    }

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):
            schema["metricas"].append(col)

        else:
            schema["dimensoes"].append(col)

    return schema