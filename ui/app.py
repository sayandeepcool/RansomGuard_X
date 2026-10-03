import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RansomGuard X", layout="wide")

st.title("🛡️ RansomGuard X - Security Dashboard")
st.markdown("### Behavioral Early-Warning & Isolation System")

col1, col2, col3 = st.columns(3)
col1.metric("System Risk", "Normal", "0%")
col2.metric("Current Stage", "Monitoring")
col3.metric("Agent Health", "Active")

st.divider()

st.subheader("Incident Timeline")
headers = {"x-token": "ransomguard_demo_token"}

try:
    response = requests.get("http://127.0.0.1:8000/incidents", headers=headers)
    if response.status_code == 200:
        incidents = response.json()
        if incidents:
            df = pd.DataFrame(incidents)
            df['Time'] = pd.to_datetime(df['ts'], unit='s')
            st.dataframe(df[['Time', 'risk', 'process', 'action', 'hash']])
        else:
            st.success("No critical security incidents detected.")
except Exception as e:
    st.warning("API Server offline. Run `uvicorn api.server:app --port 8000` to connect.")

st.divider()
st.caption("RansomGuard X runs locally. Core detection does not require Internet connectivity.")
