import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import pandas as pd
from app.services.skill_matcher import match_skills
from app.components.charts      import render_match_gauge, render_skills_donut, render_skill_badges

st.set_page_config(page_title="Skill Analysis", page_icon="📊", layout="wide")
st.title("📊 Skill Gap Analysis Dashboard")
st.markdown("Compare employee skills with role requirements.")
st.markdown("---")

# Check prerequisites
missing_steps = []
if "employee_skills" not in st.session_state:
    missing_steps.append("📄 Upload a resume on the Resume Upload page")
if "selected_role" not in st.session_state:
    missing_steps.append("🏢 Select a role on the Role Upload page")

if missing_steps:
    st.warning("Please complete these steps first:")
    for s in missing_steps:
        st.markdown(f"- {s}")
    st.stop()

# Show inputs summary
role       = st.session_state["selected_role"]
emp_skills = st.session_state["employee_skills"]

col1, col2, col3 = st.columns(3)
col1.metric("👤 Employee",        st.session_state.get("employee_name", "Employee"))
col2.metric("🏢 Target Role",     role["title"])
col3.metric("🧠 Employee Skills", len(emp_skills))

st.markdown("---")

run = st.button("🔍 Run Skill Gap Analysis", use_container_width=True, type="primary")

if run:
    with st.spinner("Running semantic skill matching..."):
        try:
            result = match_skills(
                employee_skills = emp_skills,
                required_skills = role["required_skills"],
                optional_skills = role["optional_skills"],
            )
            st.session_state["gap_report"] = result
            for key in ["learning_path", "recommendations"]:
                st.session_state.pop(key, None)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

if "gap_report" in st.session_state:
    report = st.session_state["gap_report"]

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🎯 Match Score",       f"{report['match_score']*100:.1f}%")
    k2.metric("✅ Matched Skills",     len(report["matched"]))
    k3.metric("❌ Missing Required",   len(report["missing"]))
    k4.metric("⚠️ Optional Gaps",      len(report["optional_gaps"]))

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        render_match_gauge(report["match_score"])
    with col2:
        render_skills_donut(report["matched"], report["missing"], report["optional_gaps"])

    st.markdown("---")

    # Skill badges
    col1, col2, col3 = st.columns(3)
    with col1:
        render_skill_badges(
            [m["role_skill"] for m in report["matched"]],
            "#2ecc71", "✅ Matched Skills"
        )
    with col2:
        render_skill_badges(report["missing"], "#e74c3c", "❌ Missing Skills")
    with col3:
        render_skill_badges(report["optional_gaps"], "#f39c12", "⚠️ Optional Gaps")

    st.markdown("---")

    # Similarity details
    with st.expander("🔬 Similarity Details"):
        if report["matched"]:
            rows = [{
                "Role Skill":     m["role_skill"],
                "Employee Skill": m["employee_skill"],
                "Similarity":     f"{m['similarity']*100:.1f}%",
            } for m in report["matched"]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.info("No matches found.")

    st.info("👉 Next: go to Learning Path in the sidebar.")