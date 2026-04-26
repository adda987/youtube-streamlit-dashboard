import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from style import CSS, PLOTLY_THEME, YT_COLORS

st.set_page_config(page_title="Preprocesare", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("global_youtube_statistics.csv",encoding="latin-1")

df_original =pd.read_csv("global_youtube_statistics.csv",encoding="latin-1")

st.markdown("""
<div class="page-header">
    <div class="label">04 / PREPROCESARE</div>
    <h1>Preprocesare Interactivă</h1>
</div>
""", unsafe_allow_html=True)


df = df_original.copy()

# ═══════════════════════════════════════════════════════════════════
# PASUL 1 — Valori lipsă (Cerința 4)
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header(" Tratarea valorilor lipsă")

# Situația actuală
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Situație înainte de tratare")
    missing = df.isnull().sum().reset_index()
    missing.columns = ["Coloană", "Valori lipsă"]
    missing["Procent (%)"] = (missing["Valori lipsă"] / len(df) * 100).round(2)
    missing_only = missing[missing["Valori lipsă"] > 0]
    st.dataframe(missing_only, use_container_width=True, hide_index=True)

    total_missing = int(df.isnull().sum().sum())
    pct = total_missing / (len(df) * len(df.columns)) * 100
    st.progress(pct / 100, text=f"Completitudine date: {100-pct:.1f}%")

with col_b:
    st.subheader("Alege metoda de imputare")
    metoda_earnings = st.selectbox(
        "Metoda pentru yearly_earnings_low/high",
        ["Mean", "Median", "Forward Fill (ffill)", "KNN Imputer (k=5)"],
        help="Alege cum să completezi veniturile lipsă"
    )
    metoda_uploads = st.selectbox(
        "Metoda pentru uploads",
        ["Median", "Mean", "Completează cu 0", "KNN Imputer (k=5)"],
    )

# Aplicare imputare earnings
earn_cols = ["lowest_yearly_earnings", "highest_yearly_earnings"]
if metoda_earnings == "Mean":
    for c in earn_cols:
        df[c] = df[c].fillna(df[c].mean())
elif metoda_earnings == "Median":
    for c in earn_cols:
        df[c] = df[c].fillna(df[c].median())
elif metoda_earnings == "Forward Fill (ffill)":
    for c in earn_cols:
        df[c] = df[c].ffill().bfill()
elif metoda_earnings == "KNN Imputer (k=5)":
    num_cols_knn = ["lowest_yearly_earnings", "highest_yearly_earnings", "subscribers", "video views"]
    knn = KNNImputer(n_neighbors=5)
    df[num_cols_knn] = knn.fit_transform(df[num_cols_knn])

# Aplicare imputare uploads
if metoda_uploads == "Median":
    df["uploads"] = df["uploads"].fillna(df["uploads"].median())
elif metoda_uploads == "Mean":
    df["uploads"] = df["uploads"].fillna(df["uploads"].mean())
elif metoda_uploads == "Completează cu 0":
    df["uploads"] = df["uploads"].fillna(0)
elif metoda_uploads == "KNN Imputer (k=5)":
    knn2 = KNNImputer(n_neighbors=5)
    df[["uploads", "subscribers", "video views"]] = knn2.fit_transform(
        df[["uploads", "subscribers", "video views"]]
    )

st.subheader("Situație după tratare")
missing_after = df.isnull().sum().sum()
col_r1, col_r2, col_r3 = st.columns(3)
col_r1.metric("Valori lipsă rămase", int(missing_after), delta=f"-{total_missing - int(missing_after)}")
col_r2.metric("Metoda earnings", metoda_earnings.split(" ")[0])
col_r3.metric("Metoda uploads", metoda_uploads.split(" ")[0])

df["yearly_earnings_avg"] = (df["lowest_yearly_earnings"] + df["highest_yearly_earnings"]) / 2

# Grafic înainte/după
fig_miss = go.Figure()
fig_miss.add_trace(go.Bar(name="Înainte", x=missing_only["Coloană"],
                           y=missing_only["Valori lipsă"], marker_color="#ff0000"))
after_vals = [df[c].isnull().sum() for c in missing_only["Coloană"]]
fig_miss.add_trace(go.Bar(name="După", x=missing_only["Coloană"],
                           y=after_vals, marker_color="#0be881"))
fig_miss.update_layout(**PLOTLY_THEME, barmode="group",
                        title="Valori lipsă — Înainte vs. După imputare",
                        height=300)
st.plotly_chart(fig_miss, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# PASUL 2 — Outlieri
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header(" Tratarea outlierilor")

metoda_outlieri = st.selectbox(
    "Metodă tratare outlieri (coloana subscribers)",
    ["Păstrează toți", "Elimină rândurile outlieri (IQR)", "Capping la percentile (1%-99%)"]
)

n_before = len(df)
Q1 = df["subscribers"].quantile(0.25)
Q3 = df["subscribers"].quantile(0.75)
IQR = Q3 - Q1

if metoda_outlieri == "Elimină rândurile outlieri (IQR)":
    df = df[
        (df["subscribers"] >= Q1 - 1.5*IQR) &
        (df["subscribers"] <= Q3 + 1.5*IQR)
    ].reset_index(drop=True)
elif metoda_outlieri == "Capping la percentile (1%-99%)":
    low  = df["subscribers"].quantile(0.01)
    high = df["subscribers"].quantile(0.99)
    df["subscribers"] = df["subscribers"].clip(low, high)

col_o1, col_o2, col_o3 = st.columns(3)
col_o1.metric("Rânduri înainte", n_before)
col_o2.metric("Rânduri după", len(df), delta=f"{len(df)-n_before}")
col_o3.metric("Q1-Q3 subscribers", f"{Q1/1e6:.1f}M – {Q3/1e6:.1f}M")

# ═══════════════════════════════════════════════════════════════════
# PASUL 3 — Encoding variabile categoriale (Cerința 5)
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header(" Encoding variabile categoriale")


col_e1, col_e2 = st.columns(2)
with col_e1:
    enc_category = st.selectbox("Encoding pentru 'category'",
                                ["Label Encoding", "One-Hot Encoding (get_dummies)"])
with col_e2:
    enc_country = st.selectbox("Encoding pentru 'Country'",
                               ["Label Encoding", "One-Hot Encoding (get_dummies)"])

df_enc = df.copy()
le_cat = LabelEncoder()
le_cou = LabelEncoder()

# Encoding category
if enc_category == "Label Encoding":
    df_enc["category_enc"] = le_cat.fit_transform(df_enc["category"])
    cat_mapping = pd.DataFrame({
        "Categorie": le_cat.classes_,
        "Cod numeric": range(len(le_cat.classes_))
    })
    st.markdown("**Mapping category (Label Encoding):**")
    st.dataframe(cat_mapping, use_container_width=True, hide_index=True)
else:
    dummies_cat = pd.get_dummies(df_enc["category"], prefix="cat")
    df_enc = pd.concat([df_enc, dummies_cat], axis=1)
    st.markdown(f"**One-Hot Encoding category:** {len(dummies_cat.columns)} coloane noi create")
    st.dataframe(dummies_cat.head(5), use_container_width=True, hide_index=True)

# Encoding country
if enc_country == "Label Encoding":
    df_enc["country_enc"] = le_cou.fit_transform(df_enc["Country"])
    cou_mapping = pd.DataFrame({
        "Țară": le_cou.classes_,
        "Cod numeric": range(len(le_cou.classes_))
    })
    st.markdown("**Mapping Country (Label Encoding):**")
    st.dataframe(cou_mapping, use_container_width=True, hide_index=True)
else:
    dummies_cou = pd.get_dummies(df_enc["Country"], prefix="country")
    df_enc = pd.concat([df_enc, dummies_cou], axis=1)
    st.markdown(f"**One-Hot Encoding Country:** {len(dummies_cou.columns)} coloane noi create")

# ═══════════════════════════════════════════════════════════════════
# PASUL 4 — Scalare variabile numerice (Cerința 5)
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header(" Scalare variabile numerice")


metoda_scalare = st.selectbox(
    "Metodă scalare",
    ["StandardScaler", "MinMaxScaler", "Fără scalare"]
)

scale_cols = ["subscribers", "video views", "uploads", "yearly_earnings_avg"]
df_scaled = df_enc[scale_cols].copy()

if metoda_scalare == "StandardScaler":
    scaler = StandardScaler()
    df_scaled[scale_cols] = scaler.fit_transform(df_scaled[scale_cols])
elif metoda_scalare == "MinMaxScaler":
    scaler = MinMaxScaler()
    df_scaled[scale_cols] = scaler.fit_transform(df_scaled[scale_cols])

# Vizualizare înainte / după scalare
col_s1, col_s2 = st.columns(2)
with col_s1:
    st.subheader("Înainte de scalare")
    st.dataframe(df[scale_cols].describe().round(2), use_container_width=True)
with col_s2:
    st.subheader(f"După {metoda_scalare}")
    st.dataframe(df_scaled[scale_cols].describe().round(4), use_container_width=True)

# Salvare în session_state pentru paginile ML
st.session_state["df_procesat"] = df_enc
st.session_state["df_scaled_cols"] = df_scaled
st.session_state["enc_category"] = enc_category
st.session_state["enc_country"] = enc_country
st.session_state["metoda_scalare"] = metoda_scalare

st.markdown("---")

with st.expander("Preview date preprocesate finale"):
    preview_cols = [c for c in df_enc.columns if not c.startswith("cat_") and not c.startswith("country_")]
    st.dataframe(df_enc[preview_cols].head(10), use_container_width=True, hide_index=True)
