import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from style import CSS, PLOTLY_THEME, YT_COLORS

st.set_page_config(page_title="Vizualizări", layout="wide")
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

df_full = load_data()
df = st.session_state.get("df_filtrat", df_full)

st.markdown("""
<div class="page-header">
    <div class="label">03 / VIZUALIZĂRI</div>
    <h1>Vizualizări</h1>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════
tab_mpl, tab_sns, tab_plotly = st.tabs([" Matplotlib", " Seaborn", " Plotly Interactive"])

# ──────────────────────────────────────────────────────────────────
# TAB 1 — MATPLOTLIB (Cerința 8)
# ──────────────────────────────────────────────────────────────────
with tab_mpl:
    st.markdown('<div class="sec-header">Matplotlib — grafice statistice</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Grafic 1 — Distribuție subscribers
    with col1:
        st.subheader("Distribuția subscribers")
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor("#0a0a0a")
        ax.set_facecolor("#111111")
        subs_m = df["subscribers"] / 1e6
        ax.hist(subs_m, bins=40, color="#ff0000", edgecolor="#ff6b6b", linewidth=0.5, alpha=0.85)
        ax.axvline(subs_m.mean(), color="#ffd32a", linestyle="--", linewidth=1.5,
                   label=f"Medie: {subs_m.mean():.1f}M")
        ax.axvline(subs_m.median(), color="#0be881", linestyle="--", linewidth=1.5,
                   label=f"Mediană: {subs_m.median():.1f}M")
        ax.set_xlabel("Subscribers (milioane)", color="#888", fontsize=11)
        ax.set_ylabel("Număr canale", color="#888", fontsize=11)
        ax.tick_params(colors="#888")
        ax.spines["bottom"].set_color("#272727")
        ax.spines["left"].set_color("#272727")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        legend = ax.legend(facecolor="#1a1a1a", edgecolor="#272727", labelcolor="#e8e8e8", fontsize=10)
        st.pyplot(fig, use_container_width=True)
        plt.close()

    # Grafic 2 — Bar chart top categorii
    with col2:
        st.subheader("Nr. canale pe categorie")
        cat_counts = df["category"].value_counts()
        fig2, ax2 = plt.subplots(figsize=(7, 4.5))
        fig2.patch.set_facecolor("#0a0a0a")
        ax2.set_facecolor("#111111")
        bars = ax2.barh(cat_counts.index, cat_counts.values,
                        color=YT_COLORS[:len(cat_counts)], edgecolor="none", height=0.7)
        for bar, val in zip(bars, cat_counts.values):
            ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                     str(val), va="center", color="#e8e8e8", fontsize=10)
        ax2.set_xlabel("Număr canale", color="#888", fontsize=11)
        ax2.tick_params(colors="#888")
        ax2.spines["bottom"].set_color("#272727")
        ax2.spines["left"].set_color("#272727")
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.invert_yaxis()
        st.pyplot(fig2, use_container_width=True)
        plt.close()

    # Grafic 3 — Scatter subscribers vs views cu culori pe categorie
    st.subheader("Subscribers vs. Video Views pe categorie")
    cats_uniq = df["category"].unique()
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    fig3.patch.set_facecolor("#0a0a0a")
    ax3.set_facecolor("#111111")
    for i, cat in enumerate(cats_uniq):
        sub_cat = df[df["category"] == cat]
        ax3.scatter(sub_cat["subscribers"]/1e6, sub_cat["video views"]/1e9,
                    color=YT_COLORS[i % len(YT_COLORS)], label=cat, alpha=0.7, s=25, edgecolors="none")
    ax3.set_xlabel("Subscribers (M)", color="#888", fontsize=11)
    ax3.set_ylabel("Video Views (B)", color="#888", fontsize=11)
    ax3.tick_params(colors="#888")
    for spine in ["top","right"]: ax3.spines[spine].set_visible(False)
    for spine in ["bottom","left"]: ax3.spines[spine].set_color("#272727")
    ax3.legend(facecolor="#1a1a1a", edgecolor="#272727", labelcolor="#e8e8e8",
               fontsize=9, ncol=3, bbox_to_anchor=(1,1))
    st.pyplot(fig3, use_container_width=True)
    plt.close()

# ──────────────────────────────────────────────────────────────────
# TAB 2 — SEABORN (Cerința 8)
# ──────────────────────────────────────────────────────────────────
with tab_sns:
    st.markdown('<div class="sec-header">Seaborn — heatmap, boxplot, distribuții</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Heatmap corelații
    with col1:
        st.subheader("Heatmap corelații")
        num_cols = ["subscribers", "video views", "uploads",
                    "yearly_earnings_avg", "engagement_rate"]
        corr = df[num_cols].corr()
        fig4, ax4 = plt.subplots(figsize=(6, 5))
        fig4.patch.set_facecolor("#0a0a0a")
        ax4.set_facecolor("#111111")
        cmap = sns.diverging_palette(0, 240, s=90, l=40, as_cmap=True)
        sns.heatmap(corr, annot=True, fmt=".2f", cmap=cmap, ax=ax4,
                    linewidths=0.5, linecolor="#272727",
                    annot_kws={"color": "#e8e8e8", "size": 10},
                    cbar_kws={"shrink": 0.8})
        ax4.tick_params(colors="#e8e8e8", rotation=30)
        labels = ["Subscribers", "Views", "Uploads", "Venit mediu", "Engagement"]
        ax4.set_xticklabels(labels, color="#e8e8e8", fontsize=9, rotation=30, ha="right")
        ax4.set_yticklabels(labels, color="#e8e8e8", fontsize=9, rotation=0)
        st.pyplot(fig4, use_container_width=True)
        plt.close()

    # Boxplot earnings per categorie
    with col2:
        st.subheader("Distribuție venituri pe categorie")
        fig5, ax5 = plt.subplots(figsize=(6, 5))
        fig5.patch.set_facecolor("#0a0a0a")
        ax5.set_facecolor("#111111")
        cat_order = df.groupby("category")["yearly_earnings_avg"].median().sort_values(ascending=False).index.tolist()
        palette = {cat: YT_COLORS[i % len(YT_COLORS)] for i, cat in enumerate(cat_order)}
        sns.boxplot(data=df, x="yearly_earnings_avg", y="category", order=cat_order,
                    palette=palette, ax=ax5, width=0.6, linewidth=0.8,
                    flierprops=dict(marker="o", markerfacecolor="#888", markersize=3))
        ax5.set_xlabel("Venit mediu anual ($)", color="#888", fontsize=10)
        ax5.set_ylabel("", color="#888")
        ax5.tick_params(colors="#e8e8e8", labelsize=9)
        ax5.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M"))
        for spine in ["top","right"]: ax5.spines[spine].set_visible(False)
        for spine in ["bottom","left"]: ax5.spines[spine].set_color("#272727")
        st.pyplot(fig5, use_container_width=True)
        plt.close()

    # Violin plot subscribers per tier
    st.subheader("Distribuție subscribers pe tier (violin plot)")
    fig6, ax6 = plt.subplots(figsize=(12, 4))
    fig6.patch.set_facecolor("#0a0a0a")
    ax6.set_facecolor("#111111")
    tier_order = ["Micro (<1M)", "Mid (1-5M)", "Major (5-20M)", "Mega (>20M)"]
    df_v = df.dropna(subset=["tier"])
    palette_v = {"Micro (<1M)":"#0fbcf9","Mid (1-5M)":"#0be881",
                 "Major (5-20M)":"#ffd32a","Mega (>20M)":"#ff0000"}
    sns.violinplot(data=df_v, x="tier", y="yearly_earnings_avg",
                   order=tier_order, palette=palette_v, ax=ax6,
                   inner="quartile", cut=0, linewidth=0.8)
    ax6.set_xlabel("Tier canal", color="#888", fontsize=11)
    ax6.set_ylabel("Venit mediu anual ($)", color="#888", fontsize=11)
    ax6.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x/1e6:.0f}M"))
    ax6.tick_params(colors="#e8e8e8")
    for spine in ["top","right"]: ax6.spines[spine].set_visible(False)
    for spine in ["bottom","left"]: ax6.spines[spine].set_color("#272727")
    st.pyplot(fig6, use_container_width=True)
    plt.close()

# ──────────────────────────────────────────────────────────────────
# TAB 3 — PLOTLY INTERACTIVE (Cerința 8)
# ──────────────────────────────────────────────────────────────────
with tab_plotly:
    st.subheader("Subscribers vs. Venituri anuale — interactiv")

    df_sc = df.copy()

    df_sc["subscribers_num"] = pd.to_numeric(df_sc["subscribers"], errors="coerce")
    df_sc["earnings_num"] = pd.to_numeric(df_sc["yearly_earnings_avg"], errors="coerce")

    df_sc = df_sc.replace([np.inf, -np.inf], np.nan)
    df_sc = df_sc.dropna(subset=["subscribers_num", "earnings_num", "category"])
    df_sc = df_sc[(df_sc["subscribers_num"] > 0) & (df_sc["earnings_num"] > 0)]

    if df_sc.empty:
        st.warning("Nu există suficiente date pentru acest grafic.")
    else:
        fig_sc, ax_sc = plt.subplots(figsize=(11, 6))
        fig_sc.patch.set_facecolor("#0a0a0a")
        ax_sc.set_facecolor("#111111")

        categorii = sorted(df_sc["category"].fillna("Unknown").unique())

        for i, cat in enumerate(categorii):
            dcat = df_sc[df_sc["category"].fillna("Unknown") == cat]
            ax_sc.scatter(
                dcat["subscribers_num"] / 1_000_000,
                dcat["earnings_num"] / 1_000_000,
                s=35,
                alpha=0.75,
                color=YT_COLORS[i % len(YT_COLORS)],
                label=str(cat)
            )

        ax_sc.set_xscale("log")
        ax_sc.set_yscale("log")
        ax_sc.set_xlabel("Subscribers (milioane)", color="#e8e8e8", fontsize=11)
        ax_sc.set_ylabel("Venit anual mediu (mil. $)", color="#e8e8e8", fontsize=11)
        ax_sc.tick_params(colors="#e8e8e8")
        ax_sc.grid(color="#272727", alpha=0.7)

        for spine in ["top", "right"]:
            ax_sc.spines[spine].set_visible(False)
        for spine in ["bottom", "left"]:
            ax_sc.spines[spine].set_color("#272727")

        leg = ax_sc.legend(
            facecolor="#1a1a1a",
            edgecolor="#272727",
            labelcolor="#e8e8e8",
            fontsize=8,
            ncol=2,
            loc="best"
        )

        st.pyplot(fig_sc, use_container_width=True)
        plt.close(fig_sc)

    # Grafic 2 — Bar chart venituri medii pe categorie
    st.subheader("Venit mediu anual pe categorie")
    earn_cat = df.groupby("category")["yearly_earnings_avg"].mean().sort_values(ascending=False).reset_index()
    earn_cat.columns = ["Categorie", "Venit mediu ($)"]
    fig_bar = px.bar(
        earn_cat, x="Categorie", y="Venit mediu ($)",
        color="Venit mediu ($)",
        color_continuous_scale=["#1a1a1a", "#ff6b6b", "#ff0000"],
        text_auto=".2s",
        template="plotly_dark",
    )
    fig_bar.update_layout(**PLOTLY_THEME, showlegend=False,
                          coloraxis_showscale=False)
    fig_bar.update_traces(textposition="outside", textfont_color="#e8e8e8")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Grafic 3 — Pie chart distribuție țări
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("Distribuție pe țări")
        country_cnt = df["Country"].value_counts().reset_index()
        country_cnt.columns = ["Țară", "Nr. canale"]
        fig_pie = px.pie(
            country_cnt, names="Țară", values="Nr. canale",
            color_discrete_sequence=YT_COLORS,
            hole=0.4, template="plotly_dark",
        )
        fig_pie.update_layout(**PLOTLY_THEME)
        fig_pie.update_traces(textposition="inside", textinfo="label+percent")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Grafic 4 — Box plot interactiv
    with col_p2:
        st.subheader("Distribuție engagement pe categorie")
        fig_box = px.box(
            df, x="category", y="engagement_rate",
            color="category",
            color_discrete_sequence=YT_COLORS,
            template="plotly_dark",
            labels={"category": "Categorie", "engagement_rate": "Engagement (views/sub)"},
        )
        fig_box.update_layout(**PLOTLY_THEME, showlegend=False,
                              xaxis_tickangle=-35)
        st.plotly_chart(fig_box, use_container_width=True)

    # Grafic 5 — Treemap
    st.subheader("Treemap — Canale pe țară și categorie (dimensiune = subscribers)")
    df_tree = df.dropna(subset=["Country", "category", "subscribers", "yearly_earnings_avg"])
    fig_tree = px.treemap(
        df_tree,
        path=["Country", "category"],
        values="subscribers",
        color="yearly_earnings_avg",
        color_continuous_scale=["#111111", "#ff6b6b", "#ff0000"],
        template="plotly_dark",
        color_continuous_midpoint=df_tree["yearly_earnings_avg"].median(),
    )
    fig_tree.update_layout(**PLOTLY_THEME, margin=dict(t=30, l=0, r=0, b=0))
    st.plotly_chart(fig_tree, use_container_width=True)
