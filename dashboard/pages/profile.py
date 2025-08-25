# dashboard/pages/profile.py
from datetime import datetime, date
import streamlit as st
import requests

st.set_page_config(page_title="My Profile")
st.title("My Profile")


# Check Login state
def require_login():
    if not st.session_state.get("logged_in") or not st.session_state.get("access_token"):
        st.warning("You must be logged in to access this page.")
        st.switch_page("pages/login.py")
        st.rerun()


require_login()


# Auto-fetch new access token
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
            st.rerun()  # Rerun, use the new token
        else:
            st.session_state.clear()
            st.error("Session expired. Please login again.")
            st.switch_page("pages/login.py")
            st.rerun()

    return response


# Get user profile
profile_url = "http://localhost:8000/api/profile/me"
res = auto_refresh("get", profile_url)

if res.status_code != 200:
    print(res.status_code)
    st.error("Failed to load profile.")
    st.stop()

profile_data = res.json()


# Age calculator
def calculate_age(birthday_str: str) -> int:
    try:
        birthday = datetime.fromisoformat(birthday_str)
        today = datetime.today()
        return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    except Exception:
        return 0


def calculate_bmi(height: float, weight: float) -> float:
    if height <= 0 or weight <= 0:
        return 0.0
    return round(weight / ((height / 100) ** 2), 1)


### Profile Content ###
profile = profile_data.get("profile", {})
birthday_str = profile.get("birthday")
height_cm = profile.get("height_cm", 0.0)
weight_kg = profile.get("weight_kg", 0.0)
age_value = calculate_age(birthday_str) if birthday_str else 0
bmi_value = calculate_bmi(height_cm, weight_kg) if height_cm and weight_kg else 0.0

with st.form("profile_form"):
    email = st.text_input("Email", value=profile_data.get("email", ""))
    name = st.text_input("Name", value=profile.get("name", "User"))
    birthday = st.date_input(
        "Birthday",
        value=datetime.fromisoformat(birthday_str).date() if birthday_str else date.today(),
        min_value=date(1900, 1, 1),
        max_value=date.today()
    )
    age = st.number_input("Age", value=age_value, min_value=0, disabled=True)
    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"],
        index=["Male", "Female", "Other"].index(profile.get("gender", "Other"))
    )
    height_cm = st.number_input("Height (cm)", value=profile.get("height_cm") or 0.0, min_value=0.0)
    weight_kg = st.number_input("Weight (kg)", value=profile.get("weight_kg") or 0.0, min_value=0.0)
    bmi = st.number_input("BMI", value=bmi_value, min_value=0.0, disabled=True)
    if bmi < 18.5:
        st.markdown(f"<span style='color:red'>⚠️ Underweight — Please pay attention to your nutrition.</span>", unsafe_allow_html=True)
    elif bmi < 24:
        st.markdown(f"<span style='color:black'>✅ Normal — Keep up the healthy lifestyle!</span>", unsafe_allow_html=True)
    elif bmi < 27:
        st.markdown(f"<span style='color:orange'>⚠️ Slightly Overweight — Time to move more and stay active!</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:red'>❗ Obese — Consider improving your diet and exercise habits</span>", unsafe_allow_html=True)
    
    body_fat = st.number_input(
        "Body Fat (%)",
        value=profile.get("body_fat_percent") or 0.0,
        min_value=0.0
    )

    submitted = st.form_submit_button("Update Profile")
    if submitted:
        payload = {
            "email": email,
            "name": name,
            "birthday": birthday.isoformat(),
            "gender": gender,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "body_fat_percent": body_fat
        }
        update_res = auto_refresh("put", profile_url, json=payload)
        if update_res.status_code == 200:
            st.success("Profile updated successfully.")
            st.rerun()
        else:
            st.error(f"Update failed: {update_res.json().get('detail', 'Unknown error')}")


# Danger Zone: Delete Account
st.markdown("---")
st.subheader("Danger Zone")

confirm = st.button("Delete My Account")
if confirm:
    delete_res = auto_refresh("delete", profile_url)
    if delete_res.status_code == 200:
        # Clean session keys（Avoid KeyError）
        for key in ["access_token", "refresh_token", "logged_in"]:
            if key in st.session_state:
                del st.session_state[key]

        st.success("Your account has been deleted.")
        st.switch_page("pages/profile.py")

    else:
        st.error(f"Delete failed: {delete_res.json().get('detail', 'Unknown error')}")
