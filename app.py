
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone

import requests


# -------------------------
# Config
# -------------------------
FLASK_API_BASE = "https://1grabintel.pythonanywhere.com"  # your running Flask app
st.set_page_config(layout="wide")


# ---- Set your secret API KEY here ----
VALID_API_KEY = st.secrets["VALID_API_KEY"]
# ---- Read API key from URL params ----
api_key = st.api_key = st.query_params.get("api_key", "")

# ---- Authentication ----
if api_key != VALID_API_KEY:
    st.error("❌ Unauthorized. Please provide a valid api_key in the URL.")
    st.stop()

CLIENT_API_KEY = api_key

# credit_url = f"{FLASK_API_BASE}/add_credits"

# # billing_url = f"{FLASK_API_BASE}/billing_log?api-key={CLIENT_API_KEY}&last_n=50"
# # resp = requests.get(billing_url)
# # print(resp.content)
# # c
# data = {"api_key" : CLIENT_API_KEY, "credits" : 1000, "billing_reference" : "Test"}
# resp = requests.post(credit_url, json = data)
# print(resp.content)
# input("-----")


credit_url = f"{FLASK_API_BASE}/remaining_credits?api-key={CLIENT_API_KEY}&last_n=50"
try:
    resp = requests.get(credit_url)
    resp.raise_for_status()
    credit_remaining_data = resp.json()
except Exception as e:
    st.error(f"Failed to fetch usage: {e}")
    credit_remaining_data = None


if credit_remaining_data:
    st.header(f"Welcome! {credit_remaining_data['Name']}")

    a,b,c,d = st.columns(4)
    a.metric("Credits Remaining", f"{credit_remaining_data['credits']}", width="content")



usage_tab, credit_tab = st.tabs(["Usage Log", "Credits Added"])

with usage_tab:
    usage_url = f"{FLASK_API_BASE}/usage?api-key={CLIENT_API_KEY}&last_n=50"
    try:
        resp = requests.get(usage_url)
        resp.raise_for_status()
        usage_data = resp.json()
    except Exception as e:
        st.error(f"Failed to fetch usage: {e}")
        usage_data = None

    if usage_data:
        num_requests = usage_data.get("total_requests", 0)
        # st.metric("Requests Since Last Payment", num_requests)

        st.subheader("Last 50 Requests")
        last_requests = usage_data.get("last_50_requests", [])
        if last_requests:

            df = pd.DataFrame(last_requests)
            df = df.drop(["api_key","id"], axis = 1)

            df['UTC Query Time'] = pd.to_datetime(df['request_datetime']).dt.strftime("%b %d %Y, %I:%M %p")

            df = df.drop(["request_datetime", "response_content"], axis = 1)

            col = "UTC Query Time"
            df = df[[col] + [c for c in df.columns if c != col]]


            column_config = {col: {'alignment': 'center'} for col in df.columns}
            st.dataframe(df, column_config= column_config)
        else:
            st.write("No recent requests available.")


with credit_tab:

    billing_url = f"{FLASK_API_BASE}/billing_log?api-key={CLIENT_API_KEY}&last_n=50"
    try:
        resp = requests.get(billing_url)
        resp.raise_for_status()
        billing_data = resp.json()
    except Exception as e:
        st.error(f"Failed to fetch billing: {e}")
        billing_data = None

    if billing_data:
        # num_requests = billing_data.get("total_requests", 0)
        # st.metric("Requests Since Last Payment", num_requests)
        last_requests = billing_data.get("last_50_requests", [])
        if last_requests:
            df = pd.DataFrame(last_requests)
            df = df.drop(["api_key","id"], axis = 1)

            df['UTC Credit Time'] = pd.to_datetime(df['timestamp']).dt.strftime("%b %d %Y, %I:%M %p")

            df = df.drop(["timestamp"], axis = 1)

            col = "UTC Credit Time"
            df = df[[col] + [c for c in df.columns if c != col]]

            column_config = {col: {'alignment': 'center'} for col in df.columns}
            st.dataframe(df, column_config= column_config)
        else:
            st.write("No recent requests available.")




