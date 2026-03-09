import streamlit as st
import pandas as pd

def apply_filters(df):
    st.sidebar.header("🔎 Filtros")
    df_f = df.copy()

    for col in df.columns:
        s = df[col]

        if pd.api.types.is_numeric_dtype(s):
            s2 = s.dropna()
            if s2.nunique() > 1:
                mn, mx = float(s2.min()), float(s2.max())
                if mn < mx:
                    val = st.sidebar.slider(col, mn, mx, (mn, mx))
                    df_f = df_f[(df_f[col] >= val[0]) & (df_f[col] <= val[1])]

        elif pd.api.types.is_datetime64_any_dtype(s):
            d = pd.to_datetime(s, errors="coerce").dropna()
            if d.nunique() > 1:
                ini, fim = st.sidebar.date_input(
                    col,
                    [d.min().date(), d.max().date()]
                )
                df_f[col] = pd.to_datetime(df_f[col], errors="coerce")
                df_f = df_f[
                    (df_f[col] >= pd.to_datetime(ini)) &
                    (df_f[col] <= pd.to_datetime(fim))
                ]

        else:
            vals = s.dropna().astype(str).unique()
            if len(vals) <= 50:
                sel = st.sidebar.multiselect(col, sorted(vals))
                if sel:
                    df_f = df_f[df_f[col].astype(str).isin(sel)]

    return df_f