import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render_match_gauge(score):
    pct   = round(score * 100, 1)
    color = "#2ecc71" if pct >= 75 else "#f39c12" if pct >= 50 else "#e74c3c"

    fig = go.Figure(go.Indicator(
        mode   = "gauge+number",
        value  = pct,
        title  = {"text": "Skill Match Score", "font": {"size": 18}},
        number = {"suffix": "%", "font": {"size": 36}},
        gauge  = {
            "axis":  {"range": [0, 100]},
            "bar":   {"color": color},
            "steps": [
                {"range": [0,  35], "color": "#fadbd8"},
                {"range": [35, 60], "color": "#fdebd0"},
                {"range": [60, 85], "color": "#d5f5e3"},
                {"range": [85,100], "color": "#a9dfbf"},
            ],
            "threshold": {"line": {"color": "black", "width": 3}, "value": 75},
        },
    ))
    fig.update_layout(height=280, margin=dict(t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)


def render_skills_donut(matched, missing, optional_gaps):
    fig = go.Figure(go.Pie(
        labels   = ["Matched", "Missing", "Optional Gaps"],
        values   = [len(matched), len(missing), len(optional_gaps)],
        hole     = 0.55,
        marker   = dict(colors=["#2ecc71", "#e74c3c", "#f39c12"]),
        textinfo = "label+value",
    ))
    fig.update_layout(title="Skills Breakdown", height=300, margin=dict(t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)


def render_skill_badges(skills, color, label):
    st.markdown(f"**{label}** ({len(skills)})")
    if not skills:
        st.caption("None")
        return
    html = " ".join(
        f'<span style="background:{color};color:white;padding:4px 12px;'
        f'border-radius:14px;margin:3px;display:inline-block;font-size:13px;">{s}</span>'
        for s in sorted(skills)
    )
    st.markdown(html, unsafe_allow_html=True)


def render_timeline(weeks):
    rows = []
    for w in weeks:
        for m in w.get("modules", []):
            rows.append({
                "Week":   f"Week {w['week']}",
                "Module": m.get("title", ""),
                "Skill":  m.get("skill", ""),
                "Hours":  m.get("hours_this_week", 0),
            })
    if not rows:
        st.info("No modules to display.")
        return
    df  = pd.DataFrame(rows)
    fig = px.bar(
        df, x="Hours", y="Week", color="Skill",
        orientation="h", text="Module",
        title="Weekly Learning Schedule",
        height=max(300, len(weeks) * 60)
    )
    fig.update_layout(barmode="stack", yaxis={"autorange": "reversed"})
    st.plotly_chart(fig, use_container_width=True)


def render_module_card(module, skill=""):
    icons = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
    diff  = module.get("difficulty", "beginner")
    hours = module.get("hours") or module.get("hours_this_week") or "N/A"
    url   = module.get("url", "#")
    link  = f'<a href="{url}" target="_blank" style="font-size:13px;">🔗 Open Course</a>'

    st.markdown(
        f"""
        <div style="border:1px solid #ddd;border-radius:8px;padding:14px;
                    margin-bottom:10px;background:#fafafa;">
          <div style="font-weight:600;font-size:15px;">{module.get("title","")}</div>
          <div style="color:#555;font-size:13px;margin-top:5px;">
            🏷️ <b>{skill or module.get("skill","")}</b> &nbsp;|&nbsp;
            {icons.get(diff,"⚪")} {diff.capitalize()} &nbsp;|&nbsp;
            🕐 {hours}h &nbsp;|&nbsp;
            📚 {module.get("provider","")}
          </div>
          <div style="color:#444;font-size:13px;margin-top:6px;">{module.get("description","")}</div>
          <div style="margin-top:8px;">{link}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )