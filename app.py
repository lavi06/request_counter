
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone

import requests


# -------------------------
# Config
# -------------------------
FLASK_API_BASE = "https://1grabintel.pythonanywhere.com"  # your running Flask app
# FLASK_API_BASE = "http://127.0.0.1:5000"  # your running Flask app


st.set_page_config(layout="wide")


# ---- Set your secret API KEY here ----
VALID_API_KEY = st.secrets("VALID_API_KEY")


# ---- Read API key from URL params ----
api_key = st.api_key = st.query_params.get("api_key", "")


# ---- Authentication ----
if api_key != VALID_API_KEY:
    st.error("❌ Unauthorized. Please provide a valid api_key in the URL.")
    st.stop()


CLIENT_API_KEY = VALID_API_KEY

# ##### LOGIC TO ADD CREDITS
# credit_url = f"{FLASK_API_BASE}/add_credits"
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

        st.subheader("Last 50 Requests")
        last_requests = usage_data.get("last_50_requests", [])
        if last_requests:

            df = pd.DataFrame(last_requests)



            df['UTC Query Time'] = pd.to_datetime(df['request_datetime']).dt.strftime("%b %d %Y, %I:%M %p")


            for col in ["api_key", "id", "request_datetime", "response_content"]:
                try: df = df.drop([col], axis = 1)
                except: pass


            col = ["UTC Query Time", "credit_deducted","website", "query_params", "response_status"]
            df = df[col + [c for c in df.columns if c not in col]]


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


# # -------------------------
# # 2. Payment Simulation
# # -------------------------
# st.subheader("Mark Payment")

# payment_amount = st.number_input("Payment Amount ($)", min_value=0.0, value=10.0, step=1.0)

# if st.button("Confirm Payment"):
#     try:
#         # Call Flask API to record payment
#         payment_url = f"{FLASK_API_BASE}/record_payment"
#         payload = {
#             "api_key": CLIENT_API_KEY,
#             "amount_paid": payment_amount
#         }
#         pay_resp = requests.post(payment_url, json=payload)
#         pay_resp.raise_for_status()
#         st.success("Payment recorded successfully!")
#     except Exception as e:
#         st.error(f"Failed to record payment: {e}")
