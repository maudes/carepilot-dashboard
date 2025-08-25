from datetime import date
import streamlit as st
import requests

st.set_page_config(page_title="My Daily Record")
st.title("My Daily Record")


# Check Login state
def require_login():
    if not st.session_state.get("logged_in") or not st.session_state.get("access_token"):
        st.warning("You must be logged in to access this page.")
        st.switch_page("pages/login.py")
        st.rerun()


require_login()


# Auto-refresh access token
def auto_refresh(method, url, json=None):
    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.request(method, url, headers=headers, json=json)

    if response.status_code == 401 and refresh_token:
        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        refresh_res = requests.post("http://localhost:8000/api/auth/token-refresh", headers=refresh_headers)

        if refresh_res.status_code == 200:
            new_token = refresh_res.json().get("access_token")
            st.session_state["access_token"] = new_token
            st.session_state["logged_in"] = True
            st.rerun()  # 重新執行整個 app，下一輪會用新的 access_token
        else:
            st.session_state.clear()
            st.error("Session expired. Please login again.")
            st.switch_page("pages/login.py")
            st.rerun()

    return response


# API endpoint
record_url = "http://localhost:8000/api/record/today"


# Get Today's Record
res = auto_refresh("get", record_url)
record_data = res.json() if res.status_code == 200 else {}
is_existing_record = "id" in record_data  # Check if the record exists


def get_nested_value(data, *keys, default=None):
    """Safely extract nested values from dict."""
    for key in keys:
        data = data.get(key, {})
    return data if data else default


# Input form for today's record
with st.form("daily_record_form"):
    st.subheader("Today's Vitals & Logs")

    # Vitals
    systolic_bp = st.number_input(
        "Systolic BP",
        value=get_nested_value(record_data, "vital_sign", "systolic_bp", default=0),
        min_value=0
    )
    if systolic_bp != 0:
        if systolic_bp < 90:
            st.warning("❗ Systolic BP is critically low. Please consult a doctor.")
        elif systolic_bp > 200:
            st.warning("❗ Systolic BP is extremely high. Please consult a doctor immediately.")
        elif systolic_bp > 140:
            st.error("⚠️ Hypertension alert. Please consult a doctor or take medication.")

    diastolic_bp = st.number_input(
        "Diastolic BP",
        value=get_nested_value(record_data, "vital_sign", "diastolic_bp", default=0),
        min_value=0
    )
    if diastolic_bp != 0:
        if diastolic_bp < 60:
            st.error("⚠️ Hypotension alert. Please consult a doctor.")
        elif diastolic_bp > 90:
            st.error("⚠️ Hypertension alert. Please consult a doctor or take medication.")

    pre_glucose = st.number_input(
        "Pre-meal Glucose",
        value=get_nested_value(record_data, "vital_sign", "pre_glucose", default=0),
        min_value=0
    )
    if pre_glucose != 0:
        if pre_glucose < 60:
            st.warning("❗ Hypoglycemia alert. Please intake food.")
        elif pre_glucose > 110:
            st.error("⚠️ High pre-meal glucose.")

    post_glucose = st.number_input(
        "Post-meal Glucose",
        value=get_nested_value(record_data, "vital_sign", "post_glucose", default=0),
        min_value=0
    )
    if post_glucose != 0:
        if post_glucose < 60:
            st.warning("❗ Hypoglycemia alert. Please intake food.")
        elif post_glucose > 150:
            st.error("⚠️ High pre-meal glucose.")
    
    heart_rate = st.number_input(
        "Heart Rate",
        value=get_nested_value(record_data, "vital_sign", "heart_rate", default=0),
        min_value=0
    )
    if heart_rate != 0:
        if heart_rate < 50:
            st.warning("❗ Extremely low heart rate.Please consult a doctor.")
        elif heart_rate > 150:
            st.warning("❗ Extremely high heart rate. Please consult a doctor immediately.")

    temperature = st.number_input(
        "Temperature (°C)",
        value=round(
            float(
                get_nested_value(
                    record_data,
                    "vital_sign",
                    "temperature_celsius",
                    default=0.0,
                )
            ), 1),
        step=0.1,
        format="%.1f",
    )
    if temperature != 0:
        if temperature < 32:
            st.warning("❗ Extremely low temperature.Please consult a doctor.")
        elif temperature > 41:
            st.warning("❗ Extremely high temperature. Please consult a doctor immediately.")

    spo2 = st.number_input(
        "SpO2 (%)",
        value=get_nested_value(record_data, "vital_sign", "spo2", default=0),
        min_value=0,
        max_value=100
    )
    if spo2 != 0:
        if spo2 < 90:
            st.warning("❗ Extremely low blood oxygen saturation.Please consult a doctor.")

    # Logs
    steps = st.number_input(
        "Steps",
        value=get_nested_value(record_data, "daily_log", "steps", default=0),
        min_value=0
    )
    medication = st.checkbox(
        "Did you take medication today?",
        value=get_nested_value(record_data, "daily_log", "medication", default=False)
    )
    meals_text = st.text_area(
        "Meals",
        value=get_nested_value(record_data, "daily_log", "meals_text", default="")
    )
    appetite_level = st.slider(
        "Appetite Level",
        0,
        10,
        value=get_nested_value(record_data, "daily_log", "appetite_level", default=5)
    )
    bowel_status = st.selectbox(
        "Bowel Status",
        ["Normal", "Constipation", "Diarrhea"],
        index=["Normal", "Constipation", "Diarrhea"]
        .index(get_nested_value(record_data, "daily_log", "bowel_status", default="Normal"))
    )
    mood_rate = st.slider(
        "Mood Rate",
        0,
        10,
        value=get_nested_value(record_data, "daily_log", "mood_rate", default=5)
    )
    notes = st.text_area(
        "Notes",
        value=get_nested_value(record_data, "daily_log", "notes", default="")
    )

    submitted = st.form_submit_button("Save Record")
    if submitted:
        payload = {
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

        method = "put" if is_existing_record else "post"
        save_res = auto_refresh(method, record_url, json=payload)

        if save_res.status_code in [200, 201]:
            st.success("Record saved successfully.")
            st.rerun()
        else:
            try:
                error_detail = save_res.json().get("detail", "Unknown error")
            except requests.exceptions.JSONDecodeError:
                error_detail = f"Non-JSON response: {save_res.text[:200]}"
            st.error(f"Save failed: {error_detail}")


# Danger zone: Delete today's record
st.markdown("---")

if is_existing_record:
    confirm = st.button("Delete Today's Record")
    if confirm:
        delete_res = auto_refresh("delete", record_url)
        if delete_res.status_code == 200:
            st.success("Today's record deleted.")
            st.rerun()
        else:
            try:
                error_detail = save_res.json().get("detail", "Unknown error")
            except requests.exceptions.JSONDecodeError:
                error_detail = f"Non-JSON response: {save_res.text[:200]}"
            st.error(f"Save failed: {error_detail}")
