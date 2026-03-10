import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import pandas as pd
from app.services.recommendation import recommend_modules
from app.services.learning_path  import generate_learning_path
from app.components.charts       import render_timeline, render_module_card

st.set_page_config(page_title="Learning Path", page_icon="🗺️", layout="wide")
st.title("🗺️ Personalised Learning Roadmap")
st.markdown("Week by week training plan to close your skill gaps.")
st.markdown("---")

# Check prerequisites
if "gap_report" not in st.session_state:
    st.warning("Please run the Skill Analysis first.")
    st.stop()

report   = st.session_state["gap_report"]
missing  = report["missing"]
optional = report["optional_gaps"]

# Summary
col1, col2, col3 = st.columns(3)
col1.metric("👤 Employee",       st.session_state.get("employee_name", "Employee"))
col2.metric("🏢 Target Role",    st.session_state.get("role_title", "Role"))
col3.metric("❌ Gaps to Close",  len(missing) + len(optional))

st.markdown("---")

if not missing and not optional:
    st.success("🎉 No skill gaps detected. This employee is fully qualified for the role.")
    st.stop()

gen = st.button("🚀 Generate Learning Path", use_container_width=True, type="primary")

if gen:
    with st.spinner("Building your personalised roadmap..."):
        try:
            recs = recommend_modules(missing + optional, top_n=2)
            path = generate_learning_path(
                missing_skills = missing,
                optional_gaps  = optional,
                recommendations = recs,
            )
            st.session_state["learning_path"]   = path
            st.session_state["recommendations"] = recs
        except Exception as e:
            st.error(f"Failed to generate learning path: {e}")
            st.stop()

if "learning_path" in st.session_state:
    path  = st.session_state["learning_path"]
    recs  = st.session_state["recommendations"]
    weeks = path["weeks"]

    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("📅 Total Weeks",    path["total_weeks"])
    k2.metric("🕐 Total Hours",    f"{path['total_hours']}h")
    k3.metric("📚 Skills Covered", len(recs))

    st.markdown("---")

    # Timeline chart
    st.subheader("📊 Learning Timeline")
    render_timeline(weeks)

    st.markdown("---")

    # Week by week detail
    st.subheader("📋 Week by Week Roadmap")

    for week in weeks:
        with st.expander(
            f"Week {week['week']} — {week['theme']} | "
            f"🕐 {week['estimated_hours']}h | "
            f"Skills: {', '.join(week['skills']) or 'N/A'}",
            expanded=(week["week"] == 1),
        ):
            for module in week["modules"]:
                skill = module.get("skill", week["skills"][0] if week["skills"] else "")
                render_module_card(module, skill)

    st.markdown("---")

    # Download as CSV
    st.subheader("⬇️ Export Roadmap")
    rows = []
    for w in weeks:
        for m in w["modules"]:
            rows.append({
                "Week":       w["week"],
                "Theme":      w["theme"],
                "Skill":      m.get("skill", ""),
                "Module":     m.get("title", ""),
                "Provider":   m.get("provider", ""),
                "Difficulty": m.get("difficulty", ""),
                "Hours":      m.get("hours_this_week", ""),
                "URL":        m.get("url", ""),
            })
    if rows:
        csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
        st.download_button(
            label     = "📥 Download Roadmap as CSV",
            data      = csv,
            file_name = "learning_roadmap.csv",
            mime      = "text/csv",
        )