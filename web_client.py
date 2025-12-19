import streamlit as st
import requests
import pandas as pd
import time

# --- CONFIG ---
st.set_page_config(page_title="School Admin Panel", layout="wide", page_icon="🎓")
GATEWAY_URL = "http://127.0.0.1:8080"

# --- CSS STYLES ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
    .success-msg {
        padding: 10px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- API HELPERS ---
def api_get(endpoint):
    try:
        res = requests.get(f"{GATEWAY_URL}{endpoint}")
        return res.json() if res.status_code == 200 else []
    except: return []

def api_post(endpoint, data):
    try:
        res = requests.post(f"{GATEWAY_URL}{endpoint}", json=data)
        return res.status_code in [200, 201]
    except: return False

def api_delete(endpoint, id):
    try:
        res = requests.delete(f"{GATEWAY_URL}{endpoint}/{id}")
        return res.status_code == 200
    except: return False

# --- MAIN UI ---
st.title("🎓 School Microservices Dashboard")
st.markdown("Система управління розкладом через **API Gateway** та **Discovery Service**.")

# Tabs for better UX
tab1, tab2, tab3 = st.tabs(["📚 Класи (Classes)", "👨‍🏫 Вчителі (Teachers)", "📅 Розклад (Schedule)"])

# === TAB 1: CLASSES ===
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Список Класів")
        classes = api_get("/classes")
        if classes:
            df = pd.DataFrame(classes)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Delete Section
            st.markdown("### Видалення класу")
            c_to_del = st.selectbox("Оберіть ID для видалення", [c['id'] for c in classes], key="del_class_sel")
            if st.button(f"❌ Видалити клас ID {c_to_del}", key="del_class_btn"):
                if api_delete("/classes", c_to_del):
                    st.success("Видалено!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Помилка видалення.")
        else:
            st.info("Класи відсутні.")

    with col2:
        st.subheader("Створити Клас")
        with st.form("create_class"):
            name = st.text_input("Назва (напр. 10-A)")
            profile = st.text_input("Профіль (напр. Math)")
            submitted = st.form_submit_button("➕ Створити")
            
            if submitted:
                if not name:
                    st.warning("Введіть назву класу!")
                else:
                    # ID відправляємо 0, бекенд сам замінить
                    if api_post("/classes", {"id": 0, "name": name, "profile": profile}):
                        st.success("Клас створено!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Помилка сервера.")

# === TAB 2: TEACHERS ===
with tab2:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Список Вчителів")
        teachers = api_get("/teachers")
        if teachers:
            st.dataframe(pd.DataFrame(teachers), use_container_width=True, hide_index=True)
            
            st.markdown("### Видалення вчителя")
            t_to_del = st.selectbox("Оберіть ID", [t['id'] for t in teachers], key="del_teach_sel")
            if st.button(f"❌ Видалити вчителя ID {t_to_del}", key="del_teach_btn"):
                if api_delete("/teachers", t_to_del):
                    st.success("Видалено!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.info("Вчителі відсутні.")

    with col2:
        st.subheader("Додати Вчителя")
        with st.form("create_teacher"):
            name = st.text_input("ПІБ")
            subject = st.text_input("Предмет")
            submitted = st.form_submit_button("➕ Додати")
            
            if submitted:
                if not name:
                    st.warning("Введіть ім'я!")
                else:
                    if api_post("/teachers", {"id": 0, "fullName": name, "subject": subject}):
                        st.success("Вчителя додано!")
                        time.sleep(1)
                        st.rerun()

# === TAB 3: SCHEDULE ===
with tab3:
    st.subheader("📅 Розклад Занять")
    
    # Aggregation: Get classes for dropdown
    classes_list = api_get("/classes")
    class_map = {f"{c['name']} (ID: {c['id']})": c['id'] for c in classes_list} if classes_list else {}

    with st.expander("➕ Створити новий розклад", expanded=True):
        if not class_map:
            st.warning("Спочатку створіть класи!")
        else:
            with st.form("create_schedule"):
                c1, c2 = st.columns(2)
                with c1:
                    sel_label = st.selectbox("Клас", list(class_map.keys()))
                    sel_id = class_map[sel_label]
                    day = st.selectbox("День", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
                with c2:
                    lessons_txt = st.text_area("Уроки (через кому)", "Math, History")
                
                submitted = st.form_submit_button("Створити розклад")
                
                if submitted:
                    lessons = [l.strip() for l in lessons_txt.split(",") if l.strip()]
                    if not lessons:
                        st.error("Додайте хоча б один урок!")
                    else:
                        payload = {"id": 0, "classId": sel_id, "day": day, "lessons": lessons}
                        if api_post("/schedules", payload):
                            st.success("Розклад створено! (Class Service verified)")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Помилка. Перевірте Gateway/Discovery.")

    st.divider()
    st.subheader("Поточний Розклад")
    
    schedules = api_get("/schedules")
    if schedules:
        for s in schedules:
            c1, c2, c3 = st.columns([1, 4, 1])
            with c1:
                st.info(f"ID: {s['id']}")
            with c2:
                st.markdown(f"**{s.get('className', 'Unknown')}** | {s['day']}")
                st.caption(f"Уроки: {', '.join(s['lessons'])}")
            with c3:
                if st.button("🗑️", key=f"del_sch_{s['id']}"):
                    if api_delete("/schedules", s['id']):
                        st.success("Deleted")
                        time.sleep(0.5)
                        st.rerun()
            st.divider()
    else:
        st.info("Розклад порожній.")