import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import statsmodels.api as sm
from style import CSS, PLOTLY_THEME, YT_COLORS

st.set_page_config(page_title="Regresie & Metrici", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_data
def load_and_prepare():
    df = pd.read_csv("global_youtube_statistics.csv",encoding="latin-1")
    for c in ["lowest_yearly_earnings", "highest_yearly_earnings"]:
        df[c] = df[c].fillna(df[c].median())
    df["uploads"] = df["uploads"].fillna(df["uploads"].median())
    df["yearly_earnings_avg"] = (df["lowest_yearly_earnings"] + df["highest_yearly_earnings"]) / 2
    df["engagement_rate"] = (df["video views"] / df["subscribers"]).round(2)
    le_cat = LabelEncoder()
    le_cou = LabelEncoder()
    df["category_enc"] = le_cat.fit_transform(df["category"])
    df["country_enc"]  = le_cou.fit_transform(df["Country"])
    # log-transform pentru distribuții skewed
    df["log_subscribers"] = np.log1p(df["subscribers"])
    df["log_views"]       = np.log1p(df["video views"])
    df["log_earnings"]    = np.log1p(df["yearly_earnings_avg"])
    return df

df = load_and_prepare()

st.markdown("""
<div class="page-header">
    <div class="label">06 / REGRESIE & METRICI</div>
    <h1>Regresie Multiplă & Metrici</h1>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# CONFIGURARE MODEL
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Configurare model OLS")

col_cfg1, col_cfg2 = st.columns([2, 1])

with col_cfg1:
    available_x = [
        "log_subscribers", "log_views", "uploads",
        "engagement_rate", "category_enc", "country_enc"
    ]
    labels_x = {
        "log_subscribers": "log(Subscribers)",
        "log_views":       "log(Video Views)",
        "uploads":         "Nr. Uploads",
        "engagement_rate": "Engagement Rate",
        "category_enc":    "Categorie (encoded)",
        "country_enc":     "Țară (encoded)"
    }
    sel_features = st.multiselect(
        "Variabile independente (X)",
        available_x,
        default=["log_subscribers", "log_views", "uploads", "engagement_rate", "category_enc"],
        format_func=lambda x: labels_x[x],
        help="Alege ce variabile să includă modelul de regresie"
    )

with col_cfg2:
    target_log = st.checkbox("Aplică log pe variabila dependentă", value=True,
                              help="log(earnings) reduce skewness și îmbunătățește R²")
    add_constant = st.checkbox("Adaugă constantă (intercept)", value=True)
    test_sz = st.slider("Proporție test", 0.1, 0.4, 0.2, step=0.05)

y_col = "log_earnings" if target_log else "yearly_earnings_avg"
y_label = "log(Venit mediu anual)" if target_log else "Venit mediu anual ($)"

if len(sel_features) < 1:
    st.warning("Selectează cel puțin o variabilă independentă.")
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# ANTRENARE MODEL OLS (Cerința 10)
# ═══════════════════════════════════════════════════════════════════
df_ols = df[sel_features + [y_col]].dropna()
X_raw = df_ols[sel_features]
y_ols = df_ols[y_col]

if add_constant:
    X_ols = sm.add_constant(X_raw)
else:
    X_ols = X_raw

model = sm.OLS(y_ols, X_ols).fit()

# Train/test split pentru metrici sklearn
X_tr, X_te, y_tr, y_te = train_test_split(X_ols, y_ols, test_size=test_sz, random_state=42)
model_train = sm.OLS(y_tr, X_tr).fit()
y_pred = model_train.predict(X_te)

# ═══════════════════════════════════════════════════════════════════
# METRICI (Cerința 11)
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Metrici model")

r2    = r2_score(y_te, y_pred)
rmse  = np.sqrt(mean_squared_error(y_te, y_pred))
mae   = mean_absolute_error(y_te, y_pred)
r2_adj = model.rsquared_adj

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
col_m1.metric("R²", f"{r2:.4f}", help="Proporția varianței explicată de model (1 = perfect)")
col_m2.metric("R² ajustat", f"{r2_adj:.4f}", help="R² corectat pentru numărul de variabile")
col_m3.metric("RMSE", f"{rmse:.4f}", help="Rădăcina erorii pătratice medii")
col_m4.metric("MAE", f"{mae:.4f}", help="Eroarea absolută medie")
col_m5.metric("Obs. folosite", len(df_ols))

# ═══════════════════════════════════════════════════════════════════
# SUMMARY OLS (Cerința 10)
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Summary OLS — statsmodels")

summary_text = model.summary().as_text()
st.code(summary_text, language="text")

# ═══════════════════════════════════════════════════════════════════
# VIZUALIZARE COEFICIENȚI
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Vizualizare coeficienți și intervale de încredere")

params      = model.params.drop("const", errors="ignore")
conf_int    = model.conf_int().drop("const", errors="ignore")
pvalues     = model.pvalues.drop("const", errors="ignore")

coef_df = pd.DataFrame({
    "Feature":       params.index,
    "Coeficient":    params.values,
    "CI_low":        conf_int[0].values,
    "CI_high":       conf_int[1].values,
    "p-value":       pvalues.values,
    "Semnificativ":  pvalues.values < 0.05,
})
coef_df["Label"] = coef_df["Feature"].map(lambda x: labels_x.get(x, x))
coef_df["Culoare"] = coef_df.apply(
    lambda row: "#0be881" if (row["Semnificativ"] and row["Coeficient"] > 0)
    else ("#ff0000" if (row["Semnificativ"] and row["Coeficient"] < 0)
          else "#888888"), axis=1
)

fig_coef = go.Figure()
# Intervale de încredere
for _, row in coef_df.iterrows():
    fig_coef.add_trace(go.Scatter(
        x=[row["CI_low"], row["CI_high"]],
        y=[row["Label"], row["Label"]],
        mode="lines",
        line=dict(color=row["Culoare"], width=3),
        showlegend=False,
    ))
# Coeficienți
fig_coef.add_trace(go.Scatter(
    x=coef_df["Coeficient"],
    y=coef_df["Label"],
    mode="markers",
    marker=dict(color=coef_df["Culoare"].tolist(), size=12, symbol="circle"),
    text=coef_df.apply(lambda r: f"β={r['Coeficient']:.4f}<br>p={r['p-value']:.4f}", axis=1),
    hoverinfo="text+y",
    name="Coeficient",
    showlegend=False,
))
fig_coef.add_vline(x=0, line_dash="dash", line_color="#555555")
fig_coef.update_layout(
    **PLOTLY_THEME,
    height=max(300, len(coef_df) * 55),
    xaxis_title="Valoare coeficient",
    yaxis_title="",
    title="Coeficienți OLS cu intervale de încredere 95%<br>"
          "<span style='color:#0be881'>■ pozitiv semnificativ</span>  "
          "<span style='color:#ff0000'>■ negativ semnificativ</span>  "
          "<span style='color:#888'>■ nesemnificativ (p>0.05)</span>"
)
st.plotly_chart(fig_coef, use_container_width=True)

# Tabel coeficienți
st.subheader("Tabel coeficienți detaliat")
display_coef = coef_df[["Label", "Coeficient", "CI_low", "CI_high", "p-value", "Semnificativ"]].copy()
display_coef.columns = ["Feature", "Coeficient β", "IC 2.5%", "IC 97.5%", "p-value", "Semnificativ (p<0.05)"]
display_coef = display_coef.round(5)
st.dataframe(display_coef, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════
# GRAFICE DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Grafice diagnostice")

residuals = y_te.values - y_pred.values

col_g1, col_g2 = st.columns(2)

# Actual vs Predicted
with col_g1:
    st.subheader("Valori reale vs. prezise")
    fig_ap = px.scatter(
        x=y_te.values, y=y_pred.values,
        labels={"x": f"Real ({y_label})", "y": f"Prezis ({y_label})"},
        template="plotly_dark",
        color_discrete_sequence=["#ff0000"],
        opacity=0.6,
    )
    min_v = min(y_te.min(), y_pred.min())
    max_v = max(y_te.max(), y_pred.max())
    fig_ap.add_trace(go.Scatter(
        x=[min_v, max_v], y=[min_v, max_v],
        mode="lines", line=dict(color="#0be881", dash="dash", width=1.5),
        name="Linia perfectă (y=x)"
    ))
    fig_ap.update_layout(**PLOTLY_THEME, height=380)
    st.plotly_chart(fig_ap, use_container_width=True)

# Distribuție reziduuri
with col_g2:
    st.subheader("Distribuția reziduurilor")
    fig_res = px.histogram(
        x=residuals, nbins=40,
        labels={"x": "Reziduu"},
        template="plotly_dark",
        color_discrete_sequence=["#ff6b6b"],
    )
    fig_res.add_vline(x=0, line_dash="dash", line_color="#0be881", line_width=1.5,
                       annotation_text="0", annotation_position="top right")
    fig_res.update_layout(**PLOTLY_THEME, height=380,
                           yaxis_title="Frecvență",
                           title=f"Medie reziduuri: {residuals.mean():.4f}  |  Std: {residuals.std():.4f}")
    st.plotly_chart(fig_res, use_container_width=True)

# Reziduuri vs. valori prezise
st.subheader("Reziduuri vs. valori prezise (homoscedasticitate)")
fig_rv = px.scatter(
    x=y_pred.values, y=residuals,
    labels={"x": f"Valori prezise ({y_label})", "y": "Reziduu"},
    template="plotly_dark",
    color_discrete_sequence=["#ff9f43"],
    opacity=0.5,
)
fig_rv.add_hline(y=0, line_dash="dash", line_color="#0be881", line_width=1.5)
fig_rv.update_layout(**PLOTLY_THEME, height=350)
st.plotly_chart(fig_rv, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# INTERPRETARE REZULTATE
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Interpretarea rezultatelor")

sig_feats = coef_df[coef_df["Semnificativ"]].sort_values("Coeficient", key=abs, ascending=False)

top_predictor = sig_feats.iloc[0]['Label'] if len(sig_feats) > 0 else 'N/A'
top_coef      = f"{sig_feats.iloc[0]['Coeficient']:.4f}" if len(sig_feats) > 0 else 'N/A'

st.markdown(f"""
<div class="tip">
    <strong>Rezumat model:</strong><br>
    • R² = <strong>{r2:.4f}</strong> — modelul explică <strong>{r2*100:.1f}%</strong> din variația veniturilor.<br>
    • <strong>{len(sig_feats)}/{len(coef_df)}</strong> variabile sunt statistic semnificative (p &lt; 0.05).<br>
    • Cel mai puternic predictor: <strong>{top_predictor}</strong>).
</div>
""", unsafe_allow_html=True)