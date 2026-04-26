import streamlit as st
import pandas as pd
import numpy as np
from style import CSS

st.set_page_config(page_title="Date & Statistici", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

# ── Cerința 3: Import CSV cu pandas ───────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("global_youtube_statistics.csv",encoding="latin-1")
    df["yearly_earnings_avg"] = (
        df["lowest_yearly_earnings"].fillna(df["lowest_yearly_earnings"].median()) +
        df["highest_yearly_earnings"].fillna(df["highest_yearly_earnings"].median())
    ) / 2
    df["engagement_rate"] = (df["video views"] / df["subscribers"]).round(2)
    return df

df = load_data()

# ── Header ────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="label">01 / DATE & STATISTICI</div>
    <h1>Date & Statistici</h1>
    </div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECȚIUNEA 1 — Import & inspecție (Cerința 3)
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">Despre DATE</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Rânduri", f"{df.shape[0]:,}")
with col2:
    st.metric("Coloane", df.shape[1])
with col3:
    st.metric("Valori lipsă", int(df.isnull().sum().sum()))


n_preview = st.slider("Număr rânduri de previzualizat", 5, 50, 10)
st.dataframe(df.head(n_preview), use_container_width=True, hide_index=True)

with st.expander("Tipuri de date & valori lipsă"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Tipuri de date")
        dtypes_df = pd.DataFrame({"Coloană": df.dtypes.index, "Tip": df.dtypes.values.astype(str)})
        st.dataframe(dtypes_df, use_container_width=True, hide_index=True)
    with col_b:
        st.subheader("Valori lipsă per coloană")
        missing = df.isnull().sum().reset_index()
        missing.columns = ["Coloană", "Nr. lipsă"]
        missing["Procent (%)"] = (missing["Nr. lipsă"] / len(df) * 100).round(2)
        missing = missing[missing["Nr. lipsă"] > 0]
        st.dataframe(missing, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════
# SECȚIUNEA 2 — Statistici descriptive (Cerința 6)
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">Statistici descriptive, grupare & agregare</div>', unsafe_allow_html=True)

st.subheader("Statistici descriptive generale")
num_cols = ["subscribers", "video views", "uploads", "lowest_yearly_earnings", "highest_yearly_earnings", "yearly_earnings_avg", "engagement_rate"]
st.dataframe(df[num_cols].describe().round(2), use_container_width=True)

# Grupare și agregare
st.subheader("Grupare pe categorie — statistici agregate")
st.markdown("""
```python
# Grupare + agregare cu pandas
agg_cat = df.groupby("category").agg(
    nr_canale    = ("Youtuber", "count"),
    sub_mediu    = ("subscribers", "mean"),
    views_total  = ("video views", "sum"),
    venit_mediu  = ("yearly_earnings_avg", "mean"),
    engagement   = ("engagement_rate", "mean")
).round(0).sort_values("sub_mediu", ascending=False)
```
""")

agg_cat = df.groupby("category").agg(
    nr_canale   = ("Youtuber", "count"),
    sub_mediu   = ("subscribers", "mean"),
    views_total = ("video views", "sum"),
    venit_mediu = ("yearly_earnings_avg", "mean"),
    engagement  = ("engagement_rate", "mean")
).round(0).sort_values("sub_mediu", ascending=False).reset_index()

agg_cat.columns = ["Categorie", "Nr. canale", "Subscribers mediu", "Views totale", "Venit mediu ($)", "Engagement mediu"]
st.dataframe(agg_cat, use_container_width=True, hide_index=True)

st.subheader("Grupare pe țară — Top 10")
agg_country = df.groupby("Country").agg(
    nr_canale   = ("Youtuber", "count"),
    sub_total   = ("subscribers", "sum"),
    venit_mediu = ("yearly_earnings_avg", "mean"),
).round(0).sort_values("nr_canale", ascending=False).head(10).reset_index()
agg_country.columns = ["Țară", "Nr. canale", "Subscribers totali", "Venit mediu ($)"]
st.dataframe(agg_country, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════
# SECȚIUNEA 3 — Accesare .loc și .iloc (Cerința 7)
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">Accesare cu .loc și .iloc</div>', unsafe_allow_html=True)


tab1, tab2 = st.tabs([" Accesare cu .iloc", " Filtrare cu .loc"])

with tab1:
    col_start, col_end = st.columns(2)
    with col_start:
        start = st.number_input("Start", 0, len(df)-1, 0)
    with col_end:
        end = st.number_input("End", 1, len(df), 10)

    st.markdown(f"```python\ndf.iloc[{start}:{end}]\n```")
    st.dataframe(df.iloc[start:end], use_container_width=True, hide_index=True)

with tab2:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        cat_sel = st.selectbox("Categorie", ["Toate"] + sorted(df["category"].dropna().unique().tolist()))
    with col_f2:
        min_sub = st.number_input("Subscribers minim (M)", 0.0, 100.0, 10.0, step=1.0)

    mask = pd.Series([True] * len(df))
    if cat_sel != "Toate":
        mask = mask & (df["category"] == cat_sel)
    mask = mask & (df["subscribers"] >= min_sub * 1_000_000)

    code_loc = f"""df.loc[
    (df['category'] == '{cat_sel}') &
    (df['subscribers'] >= {int(min_sub*1e6):,}),
    ['Youtuber','category','Country','subscribers','yearly_earnings_avg']
]"""
    st.markdown(f"```python\n{code_loc}\n```")
    result = df.loc[mask, ["Youtuber", "category", "Country", "subscribers", "yearly_earnings_avg"]]
    st.info(f"Rezultat: {len(result)} canale găsite")
    st.dataframe(result, use_container_width=True, hide_index=True)
