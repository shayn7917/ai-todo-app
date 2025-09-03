import streamlit as st
from datetime import datetime
import re

st.set_page_config(page_title="AI To-Do", layout="centered")

def ai_suggest(task_text):
    """
    Simple local 'AI' heuristics to suggest priority, estimated time, and tags.
    This is a rule-based helper (no external API calls).
    """
    text = task_text.lower()
    # priority hints
    if any(w in text for w in ["urgent", "asap", "immediately", "today", "now", "critical"]):
        priority = "High"
    elif any(w in text for w in ["soon", "tomorrow", "by", "this week", "next"]):
        priority = "Medium"
    else:
        priority = "Low"

    minutes = 10
    if any(w in text for w in ["read", "skim", "review"]):
        minutes = 20
    if any(w in text for w in ["implement", "build", "develop", "code", "refactor", "deploy"]):
        minutes = 120
    if any(w in text for w in ["email", "reply", "call", "schedule"]):
        minutes = 15

    tags = []
    keywords = {
        "email": ["email", "reply", "mail"],
        "coding": ["code", "implement", "build", "bug", "feature", "refactor"],
        "research": ["read", "research", "paper", "study"],
        "meeting": ["meeting", "call", "sync", "standup"],
        "design": ["design", "ux", "ui", "prototype"],
        "deploy": ["deploy", "release", "ci", "cd", "sagemaker", "vertex", "aws", "gcp", "azure"]
    }
    for tag, keys in keywords.items():
        if any(k in text for k in keys):
            tags.append(tag)
    if not tags:
        tags = ["general"]
    return {"priority": priority, "est_minutes": minutes, "tags": tags}


if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("🧠 AI‑assisted To‑Do List")
st.write("A small Streamlit to-do app that suggests priority, estimated time, and tags from the task description.")

with st.form("add_task", clear_on_submit=True):
    task = st.text_input("Task description")
    due = st.date_input("Due date (optional)", value=None)
    submitted = st.form_submit_button("Add task")
    if submitted and task.strip():
        suggestion = ai_suggest(task)
        st.session_state.tasks.append({
            "id": datetime.utcnow().isoformat(),
            "text": task.strip(),
            "due": due.isoformat() if due else "",
            "priority": suggestion["priority"],
            "est_minutes": suggestion["est_minutes"],
            "tags": suggestion["tags"],
            "done": False
        })
        st.success("Task added with AI suggestions.")

st.markdown("---")
st.subheader("Your tasks")
if not st.session_state.tasks:
    st.info("No tasks yet — add one above!")
else:
    for i, t in enumerate(st.session_state.tasks):
        cols = st.columns([0.05, 0.7, 0.25])
        checked = cols[0].checkbox("", value=t["done"], key=f"done_{i}")
        if checked != t["done"]:
            st.session_state.tasks[i]["done"] = checked
        cols[1].markdown(f"**{t['text']}**  \nPriority: `{t['priority']}` • Est: `{t['est_minutes']}m` • Tags: `{', '.join(t['tags'])}`  \nDue: {t['due'] if t['due'] else '—'}")
        if cols[2].button("Suggest update", key=f"suggest_{i}"):
            new_sugg = ai_suggest(t["text"])
            st.session_state.tasks[i]["priority"] = new_sugg["priority"]
            st.session_state.tasks[i]["est_minutes"] = new_sugg["est_minutes"]
            st.session_state.tasks[i]["tags"] = new_sugg["tags"]
            st.experimental_rerun()
        if cols[2].button("Delete", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            st.experimental_rerun()

st.markdown("---")
st.subheader("Bulk actions")
if st.button("Clear completed tasks"):
    st.session_state.tasks = [t for t in st.session_state.tasks if not t["done"]]
    st.success("Cleared completed tasks.")

st.write("Download tasks as JSON:")
if st.button("Export tasks"):
    st.download_button("Download JSON", data=json.dumps(st.session_state.tasks, indent=2), file_name="tasks.json", mime="application/json")

st.write("Tip: Run this app locally with `streamlit run app.py`.")
