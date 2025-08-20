# dashboard/pages/profile.py
from datetime import datetime, date
import streamlit as st
import requests

st.set_page_config(page_title="My Profile")
st.title("My Profile")

# 檢查登入狀態
access_token = st.session_state.get("access_token")
if not st.session_state.get("logged_in") or not access_token:
    st.switch_page("pages/login.py")

headers = {
    "Authorization": f"Bearer {access_token}"
}

# 取得個人資料
profile_url = "http://localhost:8000/api/profile/me"
res = requests.get(profile_url, headers=headers)

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


### Profile Contend ###
profile = profile_data.get("profile", {})
birthday_str = profile.get("birthday")
age_value = calculate_age(birthday_str) if birthday_str else 0

with st.form("profile_form"):
    email = st.text_input("Email", value=profile_data.get("email", ""))
    name = st.text_input("Name", value=profile.get("name", "User"))
    birthday = st.date_input(
        "Birthday",
        value=datetime.fromisoformat(birthday_str).date() if birthday_str else date.today(),
        min_value=date(1900, 1, 1),
        max_value=date.today()
    )
    # age_value = calculate_age(birthday.isoformat())
    age = st.number_input("Age", value=age_value, min_value=0, disabled=True)
    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"],
        index=["Male", "Female", "Other"].index(profile.get("gender", "Other"))
    )
    height_cm = st.number_input("Height (cm)", value=profile.get("height_cm") or 0.0, min_value=0.0)
    weight_kg = st.number_input("Weight (kg)", value=profile.get("weight_kg") or 0.0, min_value=0.0)
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
        update_res = requests.put(profile_url, headers=headers, json=payload)
        if update_res.status_code == 200:
            st.success("Profile updated successfully.")
            st.rerun()
        else:
            st.error(f"Update failed: {update_res.json().get('detail', 'Unknown error')}")


# 危險區塊：刪除帳號
st.markdown("---")
st.subheader("Danger Zone")

if st.button("Delete My Account"):
    confirm = st.checkbox("I understand this action is irreversible.")
    if confirm:
        delete_res = requests.delete(profile_url, headers=headers)
        if delete_res.status_code == 200:
            st.session_state.clear()
            st.success("Your account has been deleted.")
            st.rerun()
        else:
            st.error(f"Delete failed: {delete_res.json().get('detail', 'Unknown error')}")
