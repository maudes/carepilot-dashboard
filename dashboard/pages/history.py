from datetime import date, timedelta
import streamlit as st
import requests

st.set_page_config(page_title="My History")
st.title("My History")


# Check login state
def require_login():
    if not st.session_state.get("logged_in") or not st.session_state.get("access_token"):
        st.warning("You must be logged in to access this page.")
        st.switch_page("pages/login.py")
        st.rerun()


require_login()


# Auto-refresh access token
def auto_refresh(method, url, json=None, params=None):
    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.request(method, url, headers=headers, json=json, params=params)

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
            st.error("Session expired. Please log in again.")
            st.switch_page("pages/login.py")
            st.rerun()

    return response


# Date selection
today = date.today()
six_months_ago = today - timedelta(days=180)
selected_date = st.date_input("Select Date", value=today, min_value=six_months_ago, max_value=today)

# Search button
if st.button("Search Record"):
    response = auto_refresh("GET", "http://localhost:8000/api/history", params={"record_date": str(selected_date)})
    if response.status_code == 200:
        st.session_state["record_data"] = response.json()
        st.session_state["record_date"] = str(selected_date)
        # No notification here
    else:
        st.session_state["record_data"] = {}
        st.session_state["record_date"] = str(selected_date)
        # Still no notification here


# Safe nested value extraction
def get_nested_value(data, *keys, default=None):
    for key in keys:
        data = data.get(key, {})
    return data if data else default


# Display form if record has been searched
record_data = st.session_state.get("record_data")
record_date = st.session_state.get("record_date")

if record_data is not None and record_date:
    with st.form("history_record_form"):
        st.subheader(f"{record_date} Record")

        # Vitals
        systolic_bp = st.number_input("Systolic BP", value=get_nested_value(record_data, "vital_sign", "systolic_bp", default=0), min_value=0)
        diastolic_bp = st.number_input("Diastolic BP", value=get_nested_value(record_data, "vital_sign", "diastolic_bp", default=0), min_value=0)
        pre_glucose = st.number_input("Pre-meal Glucose", value=get_nested_value(record_data, "vital_sign", "pre_glucose", default=0), min_value=0)
        post_glucose = st.number_input("Post-meal Glucose", value=get_nested_value(record_data, "vital_sign", "post_glucose", default=0), min_value=0)
        heart_rate = st.number_input("Heart Rate", value=get_nested_value(record_data, "vital_sign", "heart_rate", default=0), min_value=0)
        temperature = st.number_input(
            "Temperature (°C)",
            value=round(float(get_nested_value(record_data, "vital_sign", "temperature_celsius", default=0.0)), 1),
            step=0.1,
            format="%.1f"
        )
        spo2 = st.number_input("SpO2 (%)", value=get_nested_value(record_data, "vital_sign", "spo2", default=0), min_value=0, max_value=100)

        # Logs
        steps = st.number_input("Steps", value=get_nested_value(record_data, "daily_log", "steps", default=0), min_value=0)
        medication = st.checkbox("Did you take medication?", value=get_nested_value(record_data, "daily_log", "medication", default=False))
        meals_text = st.text_area("Meals", value=get_nested_value(record_data, "daily_log", "meals_text", default=""))
        appetite_level = st.slider("Appetite Level", 0, 10, value=get_nested_value(record_data, "daily_log", "appetite_level", default=5))

        bowel_options = ["Normal", "Constipation", "Diarrhea"]
        bowel_value = get_nested_value(record_data, "daily_log", "bowel_status", default="Normal")
        if bowel_value not in bowel_options:
            bowel_value = "Normal"
        bowel_status = st.selectbox("Bowel Status", bowel_options, index=bowel_options.index(bowel_value))

        mood_rate = st.slider("Mood Rate", 0, 10, value=get_nested_value(record_data, "daily_log", "mood_rate", default=5))
        notes = st.text_area("Notes", value=get_nested_value(record_data, "daily_log", "notes", default=""))

        submitted = st.form_submit_button("Save Record")
        if submitted:
            payload = {
                "record_date": record_date,
                "vital_sign": {
                    "systolic_bp": systolic_bp,
                    "diastolic_bp": diastolic_bp,
                    "pre_glucose": pre_glucose,
                    "post_glucose": post_glucose,
                    "heart_rate": heart_rate,
                    "temperature_celsius": temperature,
                    "spo2": spo2,
                },
                "daily_log": {
                    "steps": steps,
                    "medication": medication,
                    "meals_text": meals_text,
                    "appetite_level": appetite_level,
                    "bowel_status": bowel_status,
                    "mood_rate": mood_rate,
                    "notes": notes,
                }
            }

            method = "put" if "id" in record_data else "post"
            save_res = auto_refresh(method, "http://localhost:8000/api/history", json=payload, params={"record_date": record_date})

            if save_res.status_code in [200, 201]:
                st.success("Record saved successfully.")
                st.rerun()
            else:
                try:
                    error_detail = save_res.json().get("detail", "Unknown error")
                except requests.exceptions.JSONDecodeError:
                    error_detail = f"Non-JSON response: {save_res.text[:200]}"
                st.error(f"Save failed: {error_detail}")

    # Delete section
    st.markdown("---")
    if "id" in record_data:
        confirm = st.button("Delete This Record")
        if confirm:
            delete_res = auto_refresh("delete", "http://localhost:8000/api/history", params={"record_date": record_date})
            if delete_res.status_code == 200:
                st.success("Record deleted.")
                st.session_state.pop("record_data", None)
                st.rerun()
            else:
                try:
                    error_detail = delete_res.json().get("detail", "Unknown error")
                except requests.exceptions.JSONDecodeError:
                    error_detail = f"Non-JSON response: {delete_res.text[:200]}"
                st.error(f"Delete failed: {error_detail}")
