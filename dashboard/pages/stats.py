import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="My Health Statistics")
st.title("My Health Statistics")


# Check login state
def require_login():
    if not st.session_state.get("logged_in") or not st.session_state.get("access_token"):
        st.warning("You must be logged in to access this page.")
        st.switch_page("pages/login.py")
        st.rerun()


require_login()


# Auto-refresh access token
def auto_refresh(method, url, params=None):
    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.request(method, url, headers=headers, params=params)

    if response.status_code == 401 and refresh_token:
        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        refresh_res = requests.post("http://localhost:8000/api/auth/token-refresh", headers=refresh_headers)

        if refresh_res.status_code == 200:
            new_token = refresh_res.json().get("access_token")
            st.session_state["access_token"] = new_token
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.session_state.clear()
            st.error("Session expired. Please login again.")
            st.switch_page("pages/login.py")
            st.rerun()

    return response


# API endpoint
record_url = "http://localhost:8000/api/chart/me"

# Select date range
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

# Call API
params = {
    "start": start_date.isoformat(),
    "end": end_date.isoformat()
}

response = auto_refresh("get", record_url, params=params)

if response.status_code == 200:
    df = pd.DataFrame(response.json())
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    else:
        st.warning("No data available for the selected date range.")

    # Summary Section
    st.subheader("Summary Statistics")
    st.write("Descriptive statistics of your health records:")
    if len(df) >= 1 or df.columns.empty:
        st.warning("No data available for the selected date range.")
    else:
        st.dataframe(df.describe())

    st.write("Column Details:")
    column_info = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum(),
        "Unique Values": df.nunique()
    })
    st.dataframe(column_info)

    # Blood Pressure Chart
    st.subheader("Blood Pressure Over Time")
    if not df.empty and all(col in df.columns for col in ["created_at", "systolic_bp", "diastolic_bp"]):
        fig1, ax1 = plt.subplots()
        ax1.plot(df["created_at"], df["systolic_bp"], label="Systolic BP", color="red")
        ax1.plot(df["created_at"], df["diastolic_bp"], label="Diastolic BP", color="blue")
        ax1.axhline(120, color="gray", linestyle="--", label="Normal Systolic")
        ax1.axhline(80, color="gray", linestyle=":", label="Normal Diastolic")
        ax1.legend()
        st.pyplot(fig1)
    else:
        st.warning("Not enough data to plot Heart Rate chart.")

    # Heart Rate Chart
    st.subheader("Heart Rate Over Time")
    if not df.empty and all(col in df.columns for col in ["created_at", "heart_rate"]):
        fig2, ax2 = plt.subplots()
        ax2.plot(df["created_at"], df["heart_rate"], label="Heart Rate", color="green")
        ax2.axhline(75, color="gray", linestyle="--", label="Normal Heart Rate")
        ax2.legend()
        st.pyplot(fig2)
    else:
        st.warning("Not enough data to plot Heart Rate chart.")

else:
    st.error("Failed to retrieve data.")
