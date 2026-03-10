import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import pandas as pd
from app.services.resume_parser   import parse_resume, extract_email, extract_name
from app.services.skill_extractor import extract_skills
from app.components.charts        import render_skill_badges

st.set_page_config(page_title="Resume Upload", page_icon="📄", layout="wide")
st.title("📄 Resume Upload & Skill Extraction")
st.markdown("Upload a resume to automatically detect technical skills.")
st.markdown("---")

with st.form("resume_form"):
    col1, col2 = st.columns(2)
    with col1:
        name       = st.text_input("Employee Name",  placeholder="Auto detected if blank")
        email      = st.text_input("Employee Email", placeholder="Auto detected if blank")
    with col2:
        department = st.text_input("Department", placeholder="Engineering")
        uploaded   = st.file_uploader("Upload Resume — PDF or DOCX", type=["pdf", "docx"])

    submitted = st.form_submit_button("🔍 Extract Skills", use_container_width=True, type="primary")

if submitted:
    if not uploaded:
        st.error("Please upload a resume file first.")
        st.stop()

    with st.spinner("Reading resume and detecting skills..."):
        try:
            file_bytes          = uploaded.read()
            raw_text, file_type = parse_resume(file_bytes, uploaded.name)

            resolved_name  = name.strip()  or extract_name(raw_text)
            resolved_email = email.strip() or extract_email(raw_text) or "unknown@company.com"

            skills = extract_skills(raw_text)

            st.session_state["employee_name"]   = resolved_name
            st.session_state["employee_email"]  = resolved_email
            st.session_state["employee_dept"]   = department
            st.session_state["raw_text"]        = raw_text
            st.session_state["employee_skills"] = [s["skill"] for s in skills]
            st.session_state["skills_detail"]   = skills

            for key in ["gap_report", "learning_path", "recommendations"]:
                st.session_state.pop(key, None)

        except Exception as e:
            st.error(f"Error processing resume: {e}")
            st.stop()

if "employee_skills" in st.session_state:
    skills        = st.session_state["employee_skills"]
    skills_detail = st.session_state.get("skills_detail", [])

    st.success(f"✅ {len(skills)} skills detected for **{st.session_state['employee_name']}**")

    k1, k2, k3 = st.columns(3)
    k1.metric("👤 Name",         st.session_state["employee_name"])
    k2.metric("📧 Email",        st.session_state["employee_email"])
    k3.metric("🧠 Skills Found", len(skills))

    st.markdown("---")

    high  = [s["skill"] for s in skills_detail if s.get("confidence", 1) >= 0.95]
    lower = [s["skill"] for s in skills_detail if s.get("confidence", 1) <  0.95]

    render_skill_badges(high,  "#2ecc71", "✅ High Confidence Skills")
    st.markdown("")
    if lower:
        render_skill_badges(lower, "#f39c12", "⚠️ Possible Skills")

    with st.expander("🔎 Full Skill Detection Table"):
        df = pd.DataFrame(skills_detail)
        df.columns = ["Skill", "Confidence", "Detection Method"]
        df["Confidence"] = df["Confidence"].apply(lambda x: f"{x*100:.0f}%")
        st.dataframe(df, use_container_width=True)

    with st.expander("📄 Raw Resume Text"):
        st.text(st.session_state.get("raw_text", "")[:3000])

    st.info("👉 Next: go to Role Upload in the sidebar.")