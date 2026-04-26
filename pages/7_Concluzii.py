import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
st.set_page_config(page_title="Concluzii", layout="wide")

YT_COLORS = ["#ff0000", "#0fbcf9", "#0be881", "#feca57", "#a55eea", "#ff9f43"]
BG = "#0a0a0a"
CARD = "#111111"
BORDER = "#272727"
TEXT = "#f5f5f5"
MUTED = "#b3b3b3"

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor=BG,
    plot_bgcolor=CARD,
    font=dict(color=TEXT),
    margin=dict(l=30, r=30, t=50, b=30)
)

st.markdown("""
<style>
.main {
    background-color: #0a0a0a;
    color: #f5f5f5;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background: #111111;
    border: 1px solid #272727;
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 16px;
}
.kpi-card {
    background: linear-gradient(135deg, #111111 0%, #161616 100%);
    border: 1px solid #272727;
    border-radius: 18px;
    padding: 18px;
    text-align: center;
}
.kpi-title {
    color: #b3b3b3;
    font-size: 14px;
    margin-bottom: 8px;
}
.kpi-value {
    color: #ffffff;
    font-size: 30px;
    font-weight: 700;
}
.section-title {
    color: #ffffff;
    font-size: 28px;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 8px;
}
.mini-note {
    color: #b3b3b3;
    font-size: 15px;
    margin-bottom: 18px;
}
.insight {
    background: #111111;
    border-left: 5px solid #ff0000;
    padding: 14px 16px;
    border-radius: 12px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_excel("global_youtube_statistics.xlsx")

    for col in [
        "subscribers",
        "video views",
        "uploads",
        "lowest_yearly_earnings",
        "highest_yearly_earnings",
        "created_year"
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "category" in df.columns:
        df["category"] = df["category"].fillna("Unknown").astype(str)
    else:
        df["category"] = "Unknown"

    if "Country" in df.columns:
        df["Country"] = df["Country"].fillna("Unknown").astype(str)
    else:
        df["Country"] = "Unknown"

    if "Youtuber" in df.columns:
        df["Youtuber"] = df["Youtuber"].fillna("Unknown").astype(str)
    else:
        df["Youtuber"] = "Unknown"

    df["lowest_yearly_earnings"] = df.get("lowest_yearly_earnings", 0).fillna(0)
    df["highest_yearly_earnings"] = df.get("highest_yearly_earnings", 0).fillna(0)

    df["yearly_earnings_avg"] = (
        df["lowest_yearly_earnings"] + df["highest_yearly_earnings"]
    ) / 2

    if "subscribers" in df.columns and "video views" in df.columns:
        df["engagement_rate"] = np.where(
            df["subscribers"] > 0,
            df["video views"] / df["subscribers"],
            np.nan
        )
    else:
        df["engagement_rate"] = np.nan

    if "created_year" in df.columns:
        df["vechime_canal"] = 2024 - df["created_year"]
    else:
        df["vechime_canal"] = np.nan

    df = df.replace([np.inf, -np.inf], np.nan)

    return df


df = load_data()

st.title("Concluzii finale")
st.markdown(
    "<div class='mini-note'>Sinteză vizuală a principalelor rezultate obținute în analiza canalelor YouTube, cu accent pe performanță, monetizare și segmentare.</div>",
    unsafe_allow_html=True
)

total_canale = len(df)
top_categorie = df["category"].mode().iloc[0] if not df["category"].mode().empty else "N/A"
top_tara = df["Country"].mode().iloc[0] if not df["Country"].mode().empty else "N/A"
venit_mediu = pd.to_numeric(df["yearly_earnings_avg"], errors="coerce").mean()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Canale analizate</div>
        <div class="kpi-value">{total_canale}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Categorie dominantă</div>
        <div class="kpi-value" style="font-size:22px;">{top_categorie}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Țara dominantă</div>
        <div class="kpi-value" style="font-size:22px;">{top_tara}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Venit anual mediu</div>
        <div class="kpi-value" style="font-size:22px;">${venit_mediu:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='section-title'>Highlights vizuale</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    top_cat = (
        df.groupby("category", dropna=False)["yearly_earnings_avg"]
        .mean()
        .reset_index()
        .sort_values("yearly_earnings_avg", ascending=False)
        .head(6)
    )

    top_cat["category"] = top_cat["category"].fillna("Unknown").astype(str)
    top_cat["yearly_earnings_avg"] = pd.to_numeric(top_cat["yearly_earnings_avg"], errors="coerce")
    top_cat = top_cat.dropna(subset=["yearly_earnings_avg"])

    if top_cat.empty:
        st.warning("Nu există date pentru graficul categoriilor.")
    else:
        fig_cat = go.Figure(go.Bar(
            x=top_cat["yearly_earnings_avg"],
            y=top_cat["category"],
            orientation="h",
            marker_color=YT_COLORS[:len(top_cat)],
            text=[f"${x:,.0f}" for x in top_cat["yearly_earnings_avg"]],
            textposition="outside"
        ))
        fig_cat.update_layout(
            **PLOTLY_THEME,
            title="Top categorii după venitul mediu anual",
            height=360,
            showlegend=False
        )
        fig_cat.update_xaxes(title="Venit anual mediu ($)")
        fig_cat.update_yaxes(title="")
        st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    top_country = (
        df.groupby("Country", dropna=False)["subscribers"]
        .mean()
        .reset_index()
        .sort_values("subscribers", ascending=False)
        .head(6)
    )

    top_country["Country"] = top_country["Country"].fillna("Unknown").astype(str)
    top_country["subscribers"] = pd.to_numeric(top_country["subscribers"], errors="coerce")
    top_country = top_country.dropna(subset=["subscribers"])
    top_country = top_country[top_country["subscribers"] > 0]

    if top_country.empty:
        st.warning("Nu există date pentru graficul țărilor.")
    else:
        fig_country = go.Figure(data=[go.Pie(
            labels=top_country["Country"],
            values=top_country["subscribers"],
            hole=0.55,
            marker=dict(colors=YT_COLORS[:len(top_country)])
        )])
        fig_country.update_layout(
            **PLOTLY_THEME,
            title="Ponderea țărilor cu cei mai mulți subscribers medii",
            height=360
        )
        st.plotly_chart(fig_country, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    with col3:
        perf = df[["subscribers", "yearly_earnings_avg"]].copy()
        perf["subscribers"] = pd.to_numeric(perf["subscribers"], errors="coerce")
        perf["yearly_earnings_avg"] = pd.to_numeric(perf["yearly_earnings_avg"], errors="coerce")
        perf = perf.replace([np.inf, -np.inf], np.nan).dropna()
        perf = perf[(perf["subscribers"] > 0) & (perf["yearly_earnings_avg"] > 0)]

        if perf.empty:
            st.warning("Nu există date pentru relația subscribers-venituri.")
        else:
            perf["subscribers_mil"] = perf["subscribers"] / 1_000_000
            perf["earnings_mil"] = perf["yearly_earnings_avg"] / 1_000_000

            sample_perf = perf.sample(min(300, len(perf)), random_state=42)

            fig_rel, ax_rel = plt.subplots(figsize=(7, 4.2))
            fig_rel.patch.set_facecolor("#0a0a0a")
            ax_rel.set_facecolor("#111111")

            ax_rel.scatter(
                sample_perf["subscribers_mil"],
                sample_perf["earnings_mil"],
                s=28,
                alpha=0.75,
                color="#ff0000"
            )

            ax_rel.set_xscale("log")
            ax_rel.set_yscale("log")

            ax_rel.set_title("Relația dintre subscribers și venituri", color="white", fontsize=12, pad=12)
            ax_rel.set_xlabel("Subscribers (milioane)", color="white")
            ax_rel.set_ylabel("Venit anual mediu (mil. $)", color="white")

            ax_rel.tick_params(colors="white")
            ax_rel.grid(color="#333333", alpha=0.4)

            for spine in ax_rel.spines.values():
                spine.set_color("#333333")

            st.pyplot(fig_rel, use_container_width=True)
            plt.close(fig_rel)
with col4:
    venit_numeric = pd.to_numeric(df["yearly_earnings_avg"], errors="coerce")

    seg = pd.cut(
        venit_numeric,
        bins=[-1, 100000, 1000000, np.inf],
        labels=["Low", "Medium", "High"]
    )

    seg_counts = seg.value_counts().reindex(["Low", "Medium", "High"], fill_value=0).reset_index()
    seg_counts.columns = ["Segment", "Count"]
    seg_counts["Segment"] = seg_counts["Segment"].astype(str)

    if seg_counts["Count"].sum() == 0:
        st.warning("Nu există date pentru distribuția segmentelor.")
    else:
        fig_seg = go.Figure(go.Bar(
            x=seg_counts["Segment"],
            y=seg_counts["Count"],
            marker_color=["#0fbcf9", "#0be881", "#ff0000"],
            text=seg_counts["Count"],
            textposition="outside"
        ))
        fig_seg.update_layout(
            **PLOTLY_THEME,
            title="Distribuția segmentelor de venit",
            showlegend=False,
            height=360
        )
        fig_seg.update_xaxes(title="Segment")
        fig_seg.update_yaxes(title="Număr canale")
        st.plotly_chart(fig_seg, use_container_width=True)

st.markdown("<div class='section-title'>Interpretare</div>", unsafe_allow_html=True)

i1, i2 = st.columns(2)

with i1:
    st.markdown("""
    <div class="insight">
    <b>1. Popularitatea nu garantează singură profitul.</b><br><br>
    Deși există o relație pozitivă între numărul de subscribers și venituri, dispersia valorilor arată că succesul financiar este influențat și de alți factori, precum tipul de conținut și nivelul de engagement.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight">
    <b>2. Categoriile de conținut contează mult.</b><br><br>
    Anumite categorii, precum Entertainment, Music sau Gaming, tind să apară frecvent printre canalele cu performanțe ridicate, ceea ce sugerează un potențial mai mare de monetizare.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight">
    <b>3. Segmentarea evidențiază profiluri diferite.</b><br><br>
    Analiza prin clustering arată că există grupuri distincte de canale: unele foarte mari și profitabile, altele medii cu potențial de creștere și unele mai mici, aflate într-o etapă incipientă.
    </div>
    """, unsafe_allow_html=True)

with i2:
    st.markdown("""
    <div class="insight">
    <b>4. Modelul de clasificare surprinde structura generală.</b><br><br>
    Rezultatele din pagina de Machine Learning arată că modelul poate diferenția relativ bine segmentele de venit, chiar dacă apar și confuzii între clase apropiate.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight">
    <b>5. Dashboard-ul are utilitate practică.</b><br><br>
    Aplicația permite explorarea interactivă a datelor și susține luarea unor decizii bazate pe date, atât pentru analiză descriptivă, cât și pentru modelare predictivă.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight">
    <b>6. Rezultatele trebuie interpretate ca tendințe.</b><br><br>
    Valorile veniturilor sunt estimate, iar unele variabile pot conține extreme sau lipsuri. Din acest motiv, concluziile sunt relevante mai ales la nivel agregat.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='section-title'>Concluzie finală</div>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
Analiza datasetului Global YouTube Statistics arată că performanța unui canal este influențată de un mix de factori: dimensiunea audienței, categoria de conținut, engagement-ul și dinamica activității. Prin combinarea vizualizărilor interactive cu tehnici de machine learning, dashboard-ul oferă o perspectivă clară, modernă și aplicată asupra ecosistemului YouTube.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card" style="text-align:center; color:#b3b3b3;">
Proiect realizat pentru disciplina <b>Pachete Software</b> de către <b>Sfetcu Andreea</b> și <b>Scînteie Mălina</b><br>
Dashboard interactiv realizat în <b>Streamlit</b> pe baza datasetului <b>Global YouTube Statistics</b>
</div>
""", unsafe_allow_html=True)