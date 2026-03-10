import streamlit as st

st.set_page_config(
    page_title = "SkillPath",
    page_icon  = "🎯",
    layout     = "wide",
)

st.title("🎯 Skill-Based Learning Automation Platform")
st.markdown("### Automatically detect skill gaps and generate a personalised learning roadmap.")
st.markdown("---")

# Show progress status
c1, c2, c3, c4 = st.columns(4)

emp_done  = "employee_skills" in st.session_state
role_done = "selected_role"   in st.session_state
gap_done  = "gap_report"      in st.session_state
path_done = "learning_path"   in st.session_state

c1.metric("Step 1 — Resume",   "✅ Done" if emp_done  else "⏳ Pending")
c2.metric("Step 2 — Role",     "✅ Done" if role_done else "⏳ Pending")
c3.metric("Step 3 — Analysis", "✅ Done" if gap_done  else "⏳ Pending")
c4.metric("Step 4 — Roadmap",  "✅ Done" if path_done else "⏳ Pending")

st.markdown("---")

st.markdown("""
## How It Works

| Step | Page | What Happens |
|------|------|--------------|
| 1️⃣ | **Resume Upload**  | Upload PDF or DOCX — spaCy extracts all skills |
| 2️⃣ | **Role Upload**    | Pick a target job role with required skills |
| 3️⃣ | **Skill Analysis** | AI compares skills and calculates match score |
| 4️⃣ | **Learning Path**  | Generates a week by week training roadmap |

## Get Started
👉 Click **Resume Upload** in the sidebar to begin.
""")

if gap_done:
    report = st.session_state["gap_report"]
    st.success(
        f"Last analysis: **{st.session_state.get('employee_name','Employee')}** vs "
        f"**{st.session_state.get('role_title','Role')}** — "
        f"Match Score: **{report['match_score']*100:.1f}%** | "
        f"Gaps: **{len(report['missing'])}** required skills missing"
    )