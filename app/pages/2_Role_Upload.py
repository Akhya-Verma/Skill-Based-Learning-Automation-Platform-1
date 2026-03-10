import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
import streamlit as st
from app.components.charts import render_skill_badges
from config.settings       import SAMPLE_ROLES_FILE

st.set_page_config(page_title="Role Upload", page_icon="🏢", layout="wide")
st.title("🏢 Job Role Requirements")
st.markdown("Choose a sample role or define your own.")
st.markdown("---")

tab1, tab2 = st.tabs(["📋 Sample Roles", "✏️ Custom Role"])

with tab1:
    with open(SAMPLE_ROLES_FILE) as f:
        sample_roles = json.load(f)

    role_titles  = [r["title"] for r in sample_roles]
    chosen_title = st.selectbox("Select a role", role_titles)
    role_data    = next(r for r in sample_roles if r["title"] == chosen_title)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Department:** {role_data['department']}")
        st.markdown(f"**Description:** {role_data['description']}")
    with col2:
        render_skill_badges(role_data["required_skills"], "#e74c3c", "🔴 Required Skills")
        st.markdown("")
        render_skill_badges(role_data["optional_skills"], "#3498db", "🔵 Optional Skills")

    if st.button("✅ Use This Role", use_container_width=True, type="primary"):
        st.session_state["selected_role"] = role_data
        st.session_state["role_title"]    = role_data["title"]
        for key in ["gap_report", "learning_path", "recommendations"]:
            st.session_state.pop(key, None)
        st.success(f"Role **{role_data['title']}** selected.")

with tab2:
    with st.form("custom_role_form"):
        col1, col2 = st.columns(2)
        with col1:
            r_title = st.text_input("Role Title",  placeholder="Senior Backend Engineer")
            r_dept  = st.text_input("Department",  placeholder="Engineering")
        with col2:
            r_desc  = st.text_area("Description", placeholder="Brief role description...", height=100)

        col3, col4 = st.columns(2)
        with col3:
            r_req = st.text_area(
                "Required Skills — one per line",
                placeholder="Python\nFastAPI\nDocker",
                height=160
            )
        with col4:
            r_opt = st.text_area(
                "Optional Skills — one per line",
                placeholder="Kubernetes\nAWS",
                height=160
            )

        save = st.form_submit_button("💾 Save and Use This Role", use_container_width=True)

    if save:
        required = [s.strip() for s in r_req.splitlines() if s.strip()]
        optional = [s.strip() for s in r_opt.splitlines() if s.strip()]
        if not r_title or not required:
            st.error("Please provide a role title and at least one required skill.")
        else:
            role_data = {
                "title":           r_title,
                "department":      r_dept,
                "description":     r_desc,
                "required_skills": required,
                "optional_skills": optional,
            }
            st.session_state["selected_role"] = role_data
            st.session_state["role_title"]    = r_title
            for key in ["gap_report", "learning_path", "recommendations"]:
                st.session_state.pop(key, None)
            st.success(f"✅ Role **{r_title}** saved with {len(required)} required skills.")

st.markdown("---")
if "selected_role" in st.session_state:
    r = st.session_state["selected_role"]
    st.success(f"**Currently selected:** {r['title']} — {len(r['required_skills'])} required, {len(r['optional_skills'])} optional skills")
    st.info("👉 Next: go to Skill Analysis in the sidebar.")
else:
    st.warning("No role selected yet. Choose one above.")