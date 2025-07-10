import streamlit as st
import pandas as pd
from supabase import create_client
import plotly.graph_objs as go
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header

# Supabase config
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- LAYOUT & DESIGN ---
st.set_page_config(page_title="Crypto Command Center", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.title("🧠 Crypto Command Center")
    st.markdown("**Solvem | Crypto Ops**")
    st.caption("Live-Datenstream aus Supabase")
    st.markdown("---")

# --- DATA LOADING ---
def fetch_table(name):
    return pd.DataFrame(supabase.table(name).select("*").execute().data)

df_major = fetch_table("Major")
df_midcap = fetch_table("Midcap")
df_mtpi = fetch_table("MTPI")
df_misc = fetch_table("MISC")
df_ema = fetch_table("EMAs")

# --- 1. MAJORS & MIDCAPS ---
majors = df_major.sort_values("created_at").iloc[-1]
midcaps = df_midcap.sort_values("created_at").iloc[-1]

major_tokens = [majors["major_1st"], majors["major_2nd"]]
midcap_tokens = [midcaps["mid_1st"], midcaps["mid_2nd"]]

# --- 2. MTPI STATUS ---
mtpi = df_mtpi.sort_values("created_at").iloc[-1]
mtpi_val = mtpi["value"]
mtpi_lower = mtpi["lower"]
mtpi_upper = mtpi["upper"]
if mtpi_val < mtpi_lower:
    mtpi_status = "Negativ"
    mtpi_color = "red"
elif mtpi_val > mtpi_upper:
    mtpi_status = "Positiv"
    mtpi_color = "green"
else:
    mtpi_status = "Neutral"
    mtpi_color = "orange"

# --- 3. SHITCOIN STATUS ---
if not df_misc.empty:
    misc = df_misc.iloc[0]
    # Zugriff wie gewohnt
else:
    st.warning("MISC-Tabelle ist leer!")
shitcoins_status = misc["TOTALE100"]
shitcoin_val = misc["TOTALE100"]
shitcoin_status = "Shitcoins Grün" if shitcoin_val == 1 else "Shitcoins Rot"
shitcoin_color = "green" if shitcoin_val == 1 else "red"

# --- 4. EMAs TABLE PREP ---
# Letzter Eintrag, EMAs für die Top-4 Token extrahieren und formatieren
df_ema_last = df_ema.sort_values("created_at").iloc[-1]
ema_tokens = [df_ema_last[f"ticker{i+1}"] for i in range(4)]
ema_results = []
for idx, ticker in enumerate(ema_tokens):
    d = {f"EMA_{tf}": df_ema_last[f"ticker{idx+1}_ema{tf}_ema12"] for tf in ["5", "15", "30", "60", "120", "240"]}
    d["Ticker"] = ticker
    d["1D"] = df_ema_last[f"ticker{idx+1}_ema1D_ema12"]
    d["3D"] = df_ema_last[f"ticker{idx+1}_ema3D_ema12"]
    ema_results.append(d)
ema_df = pd.DataFrame(ema_results).set_index("Ticker")

# --- UI LAYOUT ---
col1, col2, col3, col4 = st.columns([1.2, 1.2, 1, 2.2])

with col1:
    colored_header("Stärkste Majors", description="", color_name="blue-70")
    st.metric("Major 1st", major_tokens[0])
    st.metric("Major 2nd", major_tokens[1])
    colored_header("Stärkste Midcaps", description="", color_name="violet-70")
    st.metric("Midcap 1st", midcap_tokens[0])
    st.metric("Midcap 2nd", midcap_tokens[1])

with col2:
    colored_header("MTPI Status", description="", color_name="green-70")
    st.markdown(
        f'<div style="padding:1em;background-color:{mtpi_color};color:white;border-radius:10px;font-weight:bold;font-size:1.6em;text-align:center;">'
        f'{mtpi_status}<br><span style="font-size:0.7em;">{mtpi_val:.2f}</span></div>', unsafe_allow_html=True)
    colored_header("Shitcoin Status", description="", color_name="red-70")
    st.markdown(
        f'<div style="padding:1em;background-color:{shitcoin_color};color:white;border-radius:10px;font-weight:bold;font-size:1.3em;text-align:center;">'
        f'{shitcoin_status}</div>', unsafe_allow_html=True)

with col3:
    colored_header("Token-EMAs", description="(12er > 21er = True)", color_name="orange-70")
    st.dataframe(ema_df.style.applymap(lambda v: 'background-color:lightgreen' if v else 'background-color:#ffe4e4'))

with col4:
    colored_header("Letzte Portfolio-Snapshots", description="", color_name="gray-70")
    df_snapshots = fetch_table("portfolio_snapshots")
    if not df_snapshots.empty:
        last_n = df_snapshots.sort_values("snapshot_time", ascending=False).head(10)
        st.dataframe(last_n[["snapshot_time", "coin", "amount", "usd_value"]].rename(
            columns={"snapshot_time": "Zeit", "coin": "Coin", "amount": "Anzahl", "usd_value": "USD"}).reset_index(drop=True))
    else:
        st.info("Noch keine Portfolio-Daten")

# Styling
style_metric_cards(background="#20252B", border_left_color="#aaa", border_radius_px=10)

st.markdown("---")
st.caption("Solvem Crypto Command Center · Powered by Streamlit · Data by Supabase")
