import streamlit as st
import pandas as pd
from style import CSS

st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    layout="wide",
)

st.markdown(CSS, unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("global_youtube_statistics.csv",encoding="latin-1" )
    df["yearly_earnings_avg"] = (
        df["lowest_yearly_earnings"].fillna(0) + df["highest_yearly_earnings"].fillna(0)
    ) / 2
    return df

df = load_data()

# ── Hero ──────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">YouTube<br></div>
    <div class="hero-sub">
        Analiză completă a celor mai mari 995 de canale YouTube la nivel global.
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI metrics ───────────────────────────────────────────────────
total_subs   = df["subscribers"].sum()
total_views  = df["video views"].sum()
avg_earn     = df["yearly_earnings_avg"].mean()
top_country  = df["Country"].value_counts().index[0]
top_cat      = df["category"].value_counts().index[0]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="mc-label">Canale analizate</div>
        <div class="mc-value">{len(df):,}</div>
        <div class="mc-sub">top creatori globali</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="mc-label">Total subscribers</div>
        <div class="mc-value">{total_subs/1e9:.1f}B</div>
        <div class="mc-sub">abonați cumulați</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="mc-label">Total vizualizări</div>
        <div class="mc-value">{total_views/1e12:.1f}T</div>
        <div class="mc-sub">views cumulate</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="mc-label">Venit mediu anual</div>
        <div class="mc-value">${avg_earn/1e6:.1f}M</div>
        <div class="mc-sub">estimare per canal</div>
    </div>""", unsafe_allow_html=True)

# ── Page navigation cards ─────────────────────────────────────────
st.markdown('<div class="sec-header"> Pagini aplicație</div>', unsafe_allow_html=True)

st.markdown("""
<div class="page-grid">
    <div class="page-card">
        <div class="pc-num">01 / DATE & STATISTICI</div>
        <div class="pc-title">Date & Statistici</div>
        <div class="pc-desc">Import CSV, inspecție date, statistici descriptive, accesare cu .loc și .iloc, grupări și agregări.</div>
    </div>
    <div class="page-card">
        <div class="pc-num">02 / FILTRARE</div>
        <div class="pc-title">Filtrare Interactivă</div>
        <div class="pc-desc">Widget-uri avansate: multiselect, slider, selectbox. Filtrare dinamică pe categorie, țară și dimensiune..</div>
    </div>
    <div class="page-card">
        <div class="pc-num">03 / VIZUALIZĂRI</div>
        <div class="pc-title">Vizualizări</div>
        <div class="pc-desc">Grafice matplotlib, seaborn și plotly. Histograme, heatmap corelații, scatter, bar chart și line chart animate.</div>
    </div>
    <div class="page-card">
        <div class="pc-num">04 / PREPROCESARE</div>
        <div class="pc-title">Preprocesare</div>
        <div class="pc-desc">Tratare valori lipsă (Mean/Median/KNN), scalare StandardScaler/MinMax, encoding LabelEncoder/One-Hot.</div>
    </div>
    <div class="page-card">
        <div class="pc-num">05 / MACHINE LEARNING</div>
        <div class="pc-title">Machine Learning</div>
        <div class="pc-desc">K-Means clustering pe canale, Regresie Logistică pentru clasificarea în segmente de venit.</div>
    </div>
    <div class="page-card">
        <div class="pc-num">06 / REGRESIE & METRICI</div>
        <div class="pc-title">Regresie & Metrici</div>
        <div class="pc-desc">Regresie multiplă statsmodels: predicție venituri. R², p-values, coeficienți OLS, intervale de încredere.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── About ─────────────────────────────────────────────────────────
st.markdown('<div class="sec-header">Despre dataset</div>', unsafe_allow_html=True)
st.markdown("""
<div class="tip">
    <strong>Global YouTube Statistics 2023</strong> — conține date despre cele mai mari <strong>995 de canale</strong> 
    YouTube din lume, acoperind <strong>15 țări</strong> și <strong>11 categorii</strong> de conținut.
    Coloanele principale: <code>subscribers</code>, <code>video views</code>, <code>uploads</code>, 
    <code>category</code>, <code>Country</code>, <code>yearly_earnings_low</code>, <code>yearly_earnings_high</code>.
    Sursa originală: Kaggle — <em>Global YouTube Statistics 2023</em>.
</div>
""", unsafe_allow_html=True)
