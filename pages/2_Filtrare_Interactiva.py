import streamlit as st
import pandas as pd
import numpy as np
from style import CSS

st.set_page_config(page_title="Filtrare Interactivă", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("global_youtube_statistics.csv",encoding="latin-1")
    df["yearly_earnings_avg"] = (
        df["lowest_yearly_earnings"].fillna(df["lowest_yearly_earnings"].median()) +
        df["highest_yearly_earnings"].fillna(df["highest_yearly_earnings"].median())
    ) / 2
    df["engagement_rate"] = (df["video views"] / df["subscribers"]).round(2)
    df["tier"] = pd.cut(
        df["subscribers"],
        bins=[0, 1e6, 5e6, 20e6, np.inf],
        labels=["Micro (<1M)", "Mid (1-5M)", "Major (5-20M)", "Mega (>20M)"]
    )
    return df

df = load_data()

st.markdown("""
<div class="page-header">
    <div class="label">02 / FILTRARE INTERACTIVĂ</div>
    <h1>Filtrare Interactivă</h1>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR — Widget-uri (Cerința 2)
# ═══════════════════════════════════════════════════════════════════
st.sidebar.markdown("##  Filtre globale")
st.sidebar.markdown("---")

# Multiselect categorii
all_cats = sorted(df["category"].dropna().unique().tolist())
sel_cats = st.sidebar.multiselect(
    "Categorii",
    all_cats,
    default=all_cats,
    help="Selectează una sau mai multe categorii YouTube"
)

# Multiselect țări
all_countries = sorted(df["Country"].dropna().unique().tolist())
sel_countries = st.sidebar.multiselect(
    "Țări",
    all_countries,
    default=all_countries,
    help="Selectează țările de interes"
)

# Slider subscribers
sub_min, sub_max = int(df["subscribers"].min()), int(df["subscribers"].max())
sub_range = st.sidebar.slider(
    "Subscribers (M)",
    min_value=0.0,
    max_value=float(sub_max / 1e6),
    value=(0.0, float(sub_max / 1e6)),
    step=0.5,
    format="%.1fM"
)

# Slider engagement
eng_min = float(df["engagement_rate"].min())
eng_max = float(df["engagement_rate"].max())
eng_range = st.sidebar.slider(
    "Engagement rate (views/sub)",
    min_value=eng_min,
    max_value=eng_max,
    value=(eng_min, eng_max),
    step=1.0
)

# Selectbox tier
tiers = ["Toate"] + ["Micro (<1M)", "Mid (1-5M)", "Major (5-20M)", "Mega (>20M)"]
sel_tier = st.sidebar.selectbox("Tier canal", tiers)

# Sortare
sort_col = st.sidebar.selectbox(
    "Sortează după",
    ["subscribers", "video views", "yearly_earnings_avg", "engagement_rate", "uploads"]
)
sort_asc = st.sidebar.checkbox("Crescător", value=False)

# ═══════════════════════════════════════════════════════════════════
# Aplicare filtre cu .loc (Cerința 7)
# ═══════════════════════════════════════════════════════════════════
mask = (
    (df["category"].isin(sel_cats)) &
    (df["Country"].isin(sel_countries)) &
    (df["subscribers"] >= sub_range[0] * 1e6) &
    (df["subscribers"] <= sub_range[1] * 1e6) &
    (df["engagement_rate"] >= eng_range[0]) &
    (df["engagement_rate"] <= eng_range[1])
)
if sel_tier != "Toate":
    mask = mask & (df["tier"] == sel_tier)

df_f = df.loc[mask].sort_values(sort_col, ascending=sort_asc).reset_index(drop=True)

# ── KPI cards post-filtrare ───────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Canale filtrate", len(df_f), delta=f"{len(df_f)-len(df)} față de total")
with col2:
    st.metric("Subscribers mediu", f"{df_f['subscribers'].mean()/1e6:.1f}M")
with col3:
    st.metric("Views mediu", f"{df_f['video views'].mean()/1e9:.2f}B")
with col4:
    avg_earn = df_f['yearly_earnings_avg'].mean()
    st.metric("Venit mediu", f"${avg_earn/1e3:.0f}K")
with col5:
    st.metric("Engagement mediu", f"{df_f['engagement_rate'].mean():.0f}x")

st.markdown("---")

# ── Tabel rezultate ───────────────────────────────────────────────
st.markdown('<div class="sec-header">Rezultate filtrate</div>', unsafe_allow_html=True)

if len(df_f) == 0:
    st.warning("Nicio înregistrare nu corespunde filtrelor selectate. Ajustează filtrele din sidebar.")
else:
    show_cols = ["rank", "Youtuber", "category", "Country", "subscribers",
                 "video views", "yearly_earnings_avg", "engagement_rate", "tier"]
    display_df = df_f[show_cols].copy()
    display_df["subscribers"] = display_df["subscribers"].apply(lambda x: f"{x/1e6:.2f}M")
    display_df["video views"] = display_df["video views"].apply(lambda x: f"{x/1e9:.2f}B")
    display_df["yearly_earnings_avg"] = display_df["yearly_earnings_avg"].apply(lambda x: f"${x/1e3:.0f}K")
    display_df["engagement_rate"] = display_df["engagement_rate"].apply(lambda x: f"{x:.0f}x")
    display_df.columns = ["Rank", "Canal", "Categorie", "Țară", "Subscribers",
                          "Views", "Venit mediu", "Engagement", "Tier"]
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=500)

# ── Distribuție rezultate filtrate ───────────────────────────────
if len(df_f) > 0:
    st.markdown('<div class="sec-header">Distribuție rezultate filtrate</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        cat_counts = df_f["category"].value_counts().reset_index()
        cat_counts.columns = ["Categorie", "Nr. canale"]
        st.subheader("Pe categorie")
        st.dataframe(cat_counts, use_container_width=True, hide_index=True)
    with col_b:
        country_counts = df_f["Country"].value_counts().head(10).reset_index()
        country_counts.columns = ["Țară", "Nr. canale"]
        st.subheader("Top 10 țări")
        st.dataframe(country_counts, use_container_width=True, hide_index=True)

    # Salvare în session_state pentru Pagina 3
    st.session_state["df_filtrat"] = df_f
