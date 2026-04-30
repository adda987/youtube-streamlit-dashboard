import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, silhouette_score
)
from sklearn.impute import SimpleImputer
import time
from style import CSS, PLOTLY_THEME, YT_COLORS

st.set_page_config(page_title="Machine Learning",layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_data
def load_and_prepare():
    df = pd.read_csv("global_youtube_statistics.csv",encoding="latin-1")
    # Imputare
    for c in ["lowest_yearly_earnings", "highest_yearly_earnings"]:
        df[c] = df[c].fillna(df[c].median())
    df["uploads"] = df["uploads"].fillna(df["uploads"].median())
    df["yearly_earnings_avg"] = (df["lowest_yearly_earnings"] + df["highest_yearly_earnings"]) / 2
    df["engagement_rate"] = (df["video views"] / df["subscribers"]).round(2)
    # Encoding
    le_cat = LabelEncoder()
    le_cou = LabelEncoder()
    df["category_enc"] = le_cat.fit_transform(df["category"])
    df["country_enc"]  = le_cou.fit_transform(df["Country"])
    return df, le_cat, le_cou

df, le_cat, le_cou = load_and_prepare()

st.markdown("""
<div class="page-header">
    <div class="label">05 / MACHINE LEARNING</div>
    <h1>Machine Learning</h1>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECȚIUNEA A — K-Means Clustering (Cerința 9)
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("A.  K-Means Clustering ")


col_km1, col_km2, col_km3 = st.columns(3)
with col_km1:
    n_clusters = st.slider("Număr clustere (k)", 2, 8, 4)
with col_km2:
    km_features = st.multiselect(
        "Features pentru clustering",
        ["subscribers", "video views", "uploads", "yearly_earnings_avg", "engagement_rate", "category_enc", "country_enc"],
        default=["subscribers", "video views", "yearly_earnings_avg", "engagement_rate"]
    )
with col_km3:
    km_random = st.number_input("Random state", 0, 999, 42)

if len(km_features) < 2:
    st.warning("Selectează cel puțin 2 features pentru clustering.")
else:
    with st.spinner("Antrenez K-Means..."):
        X_km = df[km_features].dropna()
        scaler_km = StandardScaler()
        X_km_s = scaler_km.fit_transform(X_km)

        km = KMeans(n_clusters=n_clusters, random_state=km_random, n_init=10)
        labels = km.fit_predict(X_km_s)

        df_km = df.loc[X_km.index].copy()
        df_km["Cluster"] = [f"Cluster {i+1}" for i in labels]

        sil = silhouette_score(X_km_s, labels)
        inertia = km.inertia_

    # Metrici clustering
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Silhouette Score", f"{sil:.3f}", help="Aproape de 1 = clustere bine separate")
    col_m2.metric("Inertia", f"{inertia:,.0f}", help="Mai mic = clustere mai compacte")
    col_m3.metric("Clustere formate", n_clusters)

    # Scatter plot clusters
    st.subheader("Vizualizare clustere — Subscribers vs. Venituri")

    df_km_plot = df_km.copy()
    df_km_plot["subscribers_num"] = pd.to_numeric(df_km_plot["subscribers"], errors="coerce")
    df_km_plot["earnings_num"] = pd.to_numeric(df_km_plot["yearly_earnings_avg"], errors="coerce")

    df_km_plot = df_km_plot.replace([np.inf, -np.inf], np.nan)
    df_km_plot = df_km_plot.dropna(subset=["subscribers_num", "earnings_num", "Cluster"])
    df_km_plot = df_km_plot[(df_km_plot["subscribers_num"] > 0) & (df_km_plot["earnings_num"] > 0)]

    if df_km_plot.empty:
        st.warning("Nu există suficiente date pentru vizualizarea clusterelor.")
    else:
        fig_km, ax_km = plt.subplots(figsize=(11, 6))
        fig_km.patch.set_facecolor("#0a0a0a")
        ax_km.set_facecolor("#111111")

        clustere = sorted(df_km_plot["Cluster"].astype(str).unique())

        for i, cl in enumerate(clustere):
            dcl = df_km_plot[df_km_plot["Cluster"].astype(str) == cl]
            ax_km.scatter(
                dcl["subscribers_num"] / 1_000_000,
                dcl["earnings_num"] / 1_000_000,
                s=40,
                alpha=0.8,
                color=YT_COLORS[i % len(YT_COLORS)],
                label=cl
            )

        ax_km.set_xscale("log")
        ax_km.set_yscale("log")
        ax_km.set_xlabel("Subscribers (milioane)", color="#e8e8e8", fontsize=11)
        ax_km.set_ylabel("Venit anual mediu (mil. $)", color="#e8e8e8", fontsize=11)
        ax_km.tick_params(colors="#e8e8e8")
        ax_km.grid(color="#272727", alpha=0.7)

        for spine in ["top", "right"]:
            ax_km.spines[spine].set_visible(False)
        for spine in ["bottom", "left"]:
            ax_km.spines[spine].set_color("#272727")

        ax_km.legend(
            facecolor="#1a1a1a",
            edgecolor="#272727",
            labelcolor="#e8e8e8",
            fontsize=9
        )

        st.pyplot(fig_km, use_container_width=True)
        plt.close(fig_km)

    # Profil clustere
    st.subheader("Profil fiecărui cluster")
    profile_cols = ["subscribers", "video views", "yearly_earnings_avg", "engagement_rate", "uploads"]
    cluster_profile = df_km.groupby("Cluster")[profile_cols].mean().round(0)
    cluster_profile["Nr. canale"] = df_km["Cluster"].value_counts().sort_index()
    cluster_profile["Top categorie"] = df_km.groupby("Cluster")["category"].agg(lambda x: x.value_counts().index[0])
    cluster_profile["Top țară"] = df_km.groupby("Cluster")["Country"].agg(lambda x: x.value_counts().index[0])
    cluster_profile.columns = ["Subscribers mediu", "Views mediu", "Venit mediu ($)",
                                "Engagement mediu", "Uploads mediu", "Nr. canale", "Top categorie", "Top țară"]
    st.dataframe(cluster_profile, use_container_width=True)

    # Elbow method
    st.subheader("Metoda Elbow — alegerea numărului optim de clustere")
    inertias = []
    k_range = range(2, 10)
    for k in k_range:
        km_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
        km_temp.fit(X_km_s)
        inertias.append(km_temp.inertia_)

    fig_elbow = go.Figure()
    fig_elbow.add_trace(go.Scatter(
        x=list(k_range), y=inertias,
        mode="lines+markers",
        line=dict(color="#ff0000", width=2),
        marker=dict(color="#ff6b6b", size=8),
        name="Inertia"
    ))
    fig_elbow.add_vline(x=n_clusters, line_dash="dash", line_color="#ffd32a",
                         annotation_text=f"k={n_clusters} ales", annotation_position="top right")
    fig_elbow.update_layout(**PLOTLY_THEME, height=300,
                             xaxis_title="Număr clustere (k)",
                             yaxis_title="Inertia (WCSS)")
    st.plotly_chart(fig_elbow, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# SECȚIUNEA B — Regresie Logistică (Cerința 9)
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("B. Regresie Logistică ")


# Construire target
q33 = df["yearly_earnings_avg"].quantile(0.33)
q66 = df["yearly_earnings_avg"].quantile(0.66)
df["segment"] = pd.cut(
    df["yearly_earnings_avg"],
    bins=[-np.inf, q33, q66, np.inf],
    labels=["Low", "Medium", "High"]
)

col_lr1, col_lr2, col_lr3 = st.columns(3)
with col_lr1:
    lr_features = st.multiselect(
        "Features pentru Regresie Logistică",
        ["subscribers", "video views", "uploads", "engagement_rate", "category_enc", "country_enc"],
        default=["subscribers", "video views", "uploads", "engagement_rate", "category_enc"]
    )
with col_lr2:
    test_size = st.slider("Proporție test set", 0.1, 0.4, 0.2, step=0.05)
with col_lr3:
    lr_random = st.number_input("Random state LR", 0, 999, 42, key="lr_rs")
    max_iter = st.number_input("Max iterations", 100, 2000, 500, step=100)

if len(lr_features) < 2:
    st.warning("Selectează cel puțin 2 features.")
else:
    with st.spinner("Antrenez Regresia Logistică..."):
        time.sleep(0.3)
        df_lr = df[lr_features + ["segment"]].dropna()
        X_lr = df_lr[lr_features]
        y_lr = df_lr["segment"]

        scaler_lr = StandardScaler()
        X_lr_s = scaler_lr.fit_transform(X_lr)

        X_tr, X_te, y_tr, y_te = train_test_split(
            X_lr_s, y_lr, test_size=test_size, random_state=lr_random, stratify=y_lr
        )
        lr = LogisticRegression(
    max_iter=max_iter,
    random_state=lr_random
)
        lr.fit(X_tr, y_tr)
        y_pred = lr.predict(X_te)

    acc = accuracy_score(y_te, y_pred)

    # Metrici
    st.subheader("Metrici model")
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Accuracy", f"{acc:.2%}")
    col_r2.metric("Train samples", len(X_tr))
    col_r3.metric("Test samples", len(X_te))
    col_r4.metric("Clase", 3)

    col_rep, col_cm = st.columns(2)

    # Classification report
    with col_rep:
        st.subheader("Classification Report")
        report = classification_report(y_te, y_pred, output_dict=True)
        report_df = pd.DataFrame(report).T.round(3).drop("support", axis=1, errors="ignore")
        st.dataframe(report_df, use_container_width=True)

    # Confusion matrix
    with col_cm:
        st.subheader("Confusion Matrix")

        labels_cm = ["Low", "Medium", "High"]
        cm = confusion_matrix(y_te, y_pred, labels=labels_cm)

        fig_cm, ax_cm = plt.subplots(figsize=(6, 4.5))
        fig_cm.patch.set_facecolor("#0a0a0a")
        ax_cm.set_facecolor("#111111")

        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap=sns.dark_palette("#ff0000", as_cmap=True),
            cbar=False,
            xticklabels=labels_cm,
            yticklabels=labels_cm,
            annot_kws={"color": "white", "size": 14},
            linewidths=0.5,
            linecolor="#272727",
            ax=ax_cm
        )

        ax_cm.set_xlabel("Prezis", color="#e8e8e8", fontsize=11)
        ax_cm.set_ylabel("Real", color="#e8e8e8", fontsize=11)
        ax_cm.tick_params(colors="#e8e8e8")

        st.pyplot(fig_cm, use_container_width=True)
        plt.close(fig_cm)

    # Coeficienți
    st.subheader("Coeficienți regresie logistică")
    classes = lr.classes_
    coef_df = pd.DataFrame(
        lr.coef_,
        columns=lr_features,
        index=classes
    ).T

    fig_coef = go.Figure()
    colors_coef = ["#ff0000", "#0fbcf9", "#0be881"]
    for i, cls in enumerate(classes):
        fig_coef.add_trace(go.Bar(
            name=f"Segment {cls}",
            x=lr_features,
            y=coef_df[cls],
            marker_color=colors_coef[i],
        ))
    fig_coef.update_layout(**PLOTLY_THEME, barmode="group",
                            height=350,
                            xaxis_title="Feature",
                            yaxis_title="Coeficient",
                            )
    st.plotly_chart(fig_coef, use_container_width=True)

    # Distribuție predicții
    st.subheader("Distribuția predicțiilor vs. valorilor reale")

    seg_color_map = {"Low": "#0fbcf9", "Medium": "#0be881", "High": "#ff0000"}
    seg_order = ["Low", "Medium", "High"]

    y_te_series = pd.Series(list(y_te)).copy()
    y_pred_series = pd.Series(list(y_pred)).copy()

    if y_te_series.empty or y_pred_series.empty:
        st.warning("y_te sau y_pred este gol, deci distribuția nu poate fi afișată.")
    else:
        y_te_series = y_te_series.astype(str).str.strip()
        y_pred_series = y_pred_series.astype(str).str.strip()

        real_counts = pd.DataFrame({
            "Segment": seg_order,
            "Count": [(y_te_series == seg).sum() for seg in seg_order]
        })

        pred_counts = pd.DataFrame({
            "Segment": seg_order,
            "Count": [(y_pred_series == seg).sum() for seg in seg_order]
        })

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            fig_real, ax_real = plt.subplots(figsize=(5, 4))
            fig_real.patch.set_facecolor("#0a0a0a")
            ax_real.set_facecolor("#111111")

            ax_real.bar(
                real_counts["Segment"],
                real_counts["Count"],
                color=[seg_color_map[s] for s in real_counts["Segment"]]
            )

            ax_real.set_title("Valori REALE", color="white")
            ax_real.set_xlabel("Segment", color="white")
            ax_real.set_ylabel("Count", color="white")
            ax_real.tick_params(colors="white")
            ax_real.grid(axis="y", color="#272727", alpha=0.5)

            for i, v in enumerate(real_counts["Count"]):
                ax_real.text(i, v + 0.5, str(v), ha="center", color="white", fontsize=10)

            st.pyplot(fig_real, use_container_width=True)
            plt.close(fig_real)

        with col_d2:
            fig_pred, ax_pred = plt.subplots(figsize=(5, 4))
            fig_pred.patch.set_facecolor("#0a0a0a")
            ax_pred.set_facecolor("#111111")

            ax_pred.bar(
                pred_counts["Segment"],
                pred_counts["Count"],
                color=[seg_color_map[s] for s in pred_counts["Segment"]]
            )

            ax_pred.set_title("Valori PREZISE", color="white")
            ax_pred.set_xlabel("Segment", color="white")
            ax_pred.set_ylabel("Count", color="white")
            ax_pred.tick_params(colors="white")
            ax_pred.grid(axis="y", color="#272727", alpha=0.5)

            for i, v in enumerate(pred_counts["Count"]):
                ax_pred.text(i, v + 0.5, str(v), ha="center", color="white", fontsize=10)

            st.pyplot(fig_pred, use_container_width=True)
            plt.close(fig_pred)
        
