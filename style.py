CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=IBM+Plex+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    --bg:      #0a0a0a;
    --surface: #141414;
    --border:  #272727;
    --accent:  #ff0000;
    --accent2: #ff6b6b;
    --text:    #e8e8e8;
    --muted:   #888;
    --success: #3ecf8e;
    --mono:    'IBM Plex Mono', monospace;
    --display: 'Syne', sans-serif;
    --body:    'DM Sans', sans-serif;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--body) !important;
}
h1, h2, h3, h4 {
    font-family: var(--display) !important;
    color: var(--text) !important;
    letter-spacing: -0.5px;
}
[data-testid="stSidebar"] {
    background-color: #0d0d0d !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
.stAlert p { color: #0f0f0f !important; }

.hero {
    border-top: 4px solid var(--accent);
    background: var(--surface);
    padding: 48px 52px;
    border-radius: 4px;
    margin-bottom: 40px;
}
.hero-label {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--accent);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.hero-title {
    font-family: var(--display);
    font-size: 58px;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
    margin: 0 0 16px 0;
}
.hero-sub {
    font-size: 16px;
    color: #aaa;
    max-width: 600px;
    line-height: 1.6;
}

.page-header {
    border-left: 4px solid var(--accent);
    padding: 28px 36px;
    background: var(--surface);
    border-radius: 4px;
    margin-bottom: 36px;
}
.page-header .label {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--accent);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.page-header h1 {
    font-family: var(--display) !important;
    font-size: 44px !important;
    font-weight: 800;
    margin: 0 !important;
    color: var(--text) !important;
    line-height: 1.1;
}
.page-header .sub { font-size: 15px; color: #999; margin-top: 8px; }

.sec-header {
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    margin: 44px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

.tip {
    background: #111;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent2);
    border-radius: 4px;
    padding: 16px 20px;
    font-size: 14px;
    color: #ccc;
    line-height: 1.7;
}
.tip strong { color: var(--accent2); }
.tip code {
    background: #2a2a2a;
    padding: 1px 6px;
    border-radius: 3px;
    font-family: var(--mono);
    font-size: 12px;
    color: #e0e0e0;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px 24px;
    text-align: center;
}
.metric-card .mc-label {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}
.metric-card .mc-value {
    font-family: var(--display);
    font-size: 32px;
    font-weight: 800;
    color: var(--accent);
    line-height: 1;
}
.metric-card .mc-sub {
    font-size: 12px;
    color: var(--muted);
    margin-top: 4px;
}

.page-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-top: 4px;
}
.page-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 22px 26px;
    transition: border-color 0.2s;
}
.page-card:hover { border-color: var(--accent); }
.page-card .pc-num {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--accent);
    letter-spacing: 2px;
    margin-bottom: 8px;
}
.page-card .pc-title {
    font-family: var(--display);
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 6px;
}
.page-card .pc-desc { font-size: 13px; color: var(--muted); line-height: 1.6; }

.concept-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 22px 26px;
    margin-bottom: 12px;
}
.concept-box .cb-title {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.concept-box p { color: #ccc !important; font-size: 14px; line-height: 1.7; margin: 0; }
.concept-box code {
    background: #2a2a2a;
    padding: 1px 6px;
    border-radius: 3px;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--accent2);
}
</style>
"""

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#111111",
    font=dict(family="DM Sans", color="#e8e8e8"),
    xaxis=dict(gridcolor="#272727", zerolinecolor="#272727"),
    yaxis=dict(gridcolor="#272727", zerolinecolor="#272727"),
    colorway=["#ff0000","#ff6b6b","#ff9f43","#ffd32a","#0fbcf9","#0be881","#f8b739","#e84393"],
)

YT_COLORS = ["#ff0000","#ff6b6b","#ff9f43","#ffd32a","#0fbcf9",
             "#0be881","#f8b739","#e84393","#3c40c4","#575fcf","#ef5777"]
