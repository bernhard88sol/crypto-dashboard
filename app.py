import streamlit as st
import pandas as pd
from supabase import create_client

# Supabase-Zugang aus den Streamlit Secrets
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
TABLE = "portfolio_snapshots"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📈 Crypto Portfolio Dashboard")
st.caption("Live aus Supabase · powered by Streamlit Cloud")

# Hole alle Portfolio-Daten
res = supabase.table(TABLE).select("*").execute()
df = pd.DataFrame(res.data)
if df.empty:
    st.warning("Noch keine Portfolio-Daten in der Datenbank!")
    st.stop()

# Zeitfeld wandeln
df['snapshot_time'] = pd.to_datetime(df['snapshot_time'])

# Aktueller Snapshot
latest_time = df['snapshot_time'].max()
df_latest = df[df['snapshot_time'] == latest_time].sort_values('usd_value', ascending=False)

st.subheader("Portfolio zum Zeitpunkt:")
st.write(latest_time.strftime('%Y-%m-%d %H:%M:%S UTC'))

st.dataframe(df_latest[['coin', 'amount', 'usd_value']].set_index('coin'))

# Pie Chart
st.subheader("Portfolio-Verteilung (Pie-Chart)")
import plotly.express as px
fig = px.pie(df_latest, values='usd_value', names='coin', title='Portfolio-Verteilung')
st.plotly_chart(fig)

# Zeitreihe Gesamtwert
st.subheader("Portfolio-Entwicklung (Gesamtwert in USD)")
time_series = df.groupby('snapshot_time').agg({'usd_value':'sum'}).reset_index()
st.line_chart(time_series, x='snapshot_time', y='usd_value')

st.info("Letzter Import: " + str(latest_time))
