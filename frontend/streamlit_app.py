import os
import streamlit as st
import requests
import plotly.graph_objects as go

API_BASE = "https://ai-qus-backend-production-xxxx.up.railway.app"

st.set_page_config(page_title="AI QBank", layout="wide", page_icon="📚")

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-header {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .stat-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: left;
    }
    .stat-label {
        color: #6b7280;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .badge {
        display: inline-block;
        background: #ecfdf5;
        color: #059669;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-purple {
        background: #f5f3ff;
        color: #7c3aed;
    }
    div[data-testid="stSidebarNav"] { display: none; }
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    .stButton>button[kind="primary"] {
        background-color: #7c3aed;
        border-color: #7c3aed;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Auth state ----------------
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user" not in st.session_state:
    st.session_state.user = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}


# ---------------- Login / Signup gate ----------------
if not st.session_state.access_token:
    st.markdown('<p class="main-header">📚 AI QBank</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Study Companion — please log in or sign up to continue.</p>', unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    with tab_login:
        with st.form("login_form"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submitted = st.form_submit_button("Log In", type="primary")
            if login_submitted:
                resp = requests.post(
                    f"{API_BASE}/auth/login",
                    json={"email": login_email, "password": login_password},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.access_token = data["access_token"]
                    st.session_state.user = data["user"]
                    st.rerun()
                else:
                    st.error(resp.json().get("detail", "Login failed"))

    with tab_signup:
        with st.form("signup_form"):
            signup_name = st.text_input("Name", key="signup_name")
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_submitted = st.form_submit_button("Create Account", type="primary")
            if signup_submitted:
                resp = requests.post(
                    f"{API_BASE}/auth/signup",
                    json={"email": signup_email, "password": signup_password, "name": signup_name},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.access_token = data["access_token"]
                    st.session_state.user = data["user"]
                    st.rerun()
                else:
                    st.error(resp.json().get("detail", "Signup failed"))

    st.stop()

# ---------------- Session state ----------------
if "subject_id" not in st.session_state:
    st.session_state.subject_id = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### 📚 AI QBank")
    st.caption("Your Study Companion")
    if st.session_state.user:
        st.caption(f"👤 {st.session_state.user.get('name') or st.session_state.user['email']}")
        if st.button("Log out", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.user = None
            st.session_state.subject_id = None
            st.rerun()
    st.divider()

    try:
        subjects_resp = requests.get(f"{API_BASE}/subjects", headers=auth_headers())
        if subjects_resp.status_code == 401:
            st.session_state.access_token = None
            st.session_state.user = None
            st.rerun()
        subjects = subjects_resp.json() if subjects_resp.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach backend.\nIs uvicorn running on port 8080?")
        st.stop()

    subject_names = {s["id"]: s["name"] for s in subjects}

    nav_options = ["Dashboard", "Subjects", "Documents", "Upload", "Question Generation", "Ask Question", "Results"]
    page = st.radio(
        "Navigation",
        nav_options,
        index=nav_options.index(st.session_state.page),
        label_visibility="collapsed",
    )
    st.session_state.page = page

    st.divider()
    if subjects:
        options = [f"{s['id']}: {s['name']}" for s in subjects]
        default_idx = 0
        if st.session_state.subject_id:
            for i, s in enumerate(subjects):
                if s["id"] == st.session_state.subject_id:
                    default_idx = i
        choice = st.selectbox("Active Subject", options, index=default_idx)
        st.session_state.subject_id = int(choice.split(":")[0])
    else:
        st.info("No subjects yet.")

subject_id = st.session_state.subject_id

# ==================================================================
# PAGE: Dashboard
# ==================================================================
if page == "Dashboard":
    st.markdown('<p class="main-header">Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Overview of your subjects and question banks.</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Total Subjects</div>
        <div class="stat-value">{len(subjects)}</div></div>""", unsafe_allow_html=True)
    with col2:
        total_docs = 0
        for s in subjects:
            d = requests.get(f"{API_BASE}/subjects/{s['id']}/documents", headers=auth_headers())
            if d.status_code == 200:
                total_docs += len(d.json())
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Total Documents</div>
        <div class="stat-value">{total_docs}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Active Subject</div>
        <div class="stat-value" style="font-size:1.2rem;">{subject_names.get(subject_id, '—')}</div></div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("Your Subjects")
    if subjects:
        for s in subjects:
            d = requests.get(f"{API_BASE}/subjects/{s['id']}/documents", headers=auth_headers())
            doc_count = len(d.json()) if d.status_code == 200 else 0
            st.write(f"**{s['name']}** — {doc_count} documents")
    else:
        st.info("Create your first subject in the Subjects tab.")

# ==================================================================
# PAGE: Subjects
# ==================================================================
elif page == "Subjects":
    st.markdown('<p class="main-header">Subjects</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Manage your subjects and their study materials.</p>', unsafe_allow_html=True)

    with st.expander("➕ Create New Subject", expanded=(len(subjects) == 0)):
        with st.form("new_subject_form"):
            new_name = st.text_input("Subject Name")
            new_desc = st.text_area("Description (optional)")
            submitted = st.form_submit_button("Create Subject", type="primary")
            if submitted and new_name:
                resp = requests.post(f"{API_BASE}/subjects", json={"name": new_name}, headers=auth_headers())
                if resp.status_code == 200:
                    st.session_state.subject_id = resp.json()["id"]
                    st.success("Subject created successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed: {resp.text}")

    st.divider()
    if subjects:
        for s in subjects:
            d = requests.get(f"{API_BASE}/subjects/{s['id']}/documents", headers=auth_headers())
            doc_count = len(d.json()) if d.status_code == 200 else 0
            col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
            with col1:
                st.write(f"**{s['name']}**  (ID: {s['id']})")
            with col2:
                st.write(f"{doc_count} documents")
            with col3:
                if st.button("Select", key=f"select_{s['id']}"):
                    st.session_state.subject_id = s["id"]
                    st.session_state.page = "Upload"
                    st.rerun()
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{s['id']}"):
                    st.session_state[f"confirm_delete_{s['id']}"] = True

            if st.session_state.get(f"confirm_delete_{s['id']}"):
                st.warning(f"Delete **{s['name']}** and all its documents, analysis, and generated questions? This cannot be undone.")
                col_yes, col_no = st.columns([1, 4])
                with col_yes:
                    if st.button("Yes, delete", key=f"confirm_yes_{s['id']}", type="primary"):
                        resp = requests.delete(f"{API_BASE}/subjects/{s['id']}", headers=auth_headers())
                        if resp.status_code == 200:
                            st.success("Deleted.")
                            if st.session_state.subject_id == s["id"]:
                                st.session_state.subject_id = None
                            del st.session_state[f"confirm_delete_{s['id']}"]
                            st.rerun()
                        else:
                            st.error(resp.text)
                with col_no:
                    if st.button("Cancel", key=f"confirm_no_{s['id']}"):
                        del st.session_state[f"confirm_delete_{s['id']}"]
                        st.rerun()
    else:
        st.info("No subjects yet — create one above.")

# ==================================================================
# PAGE: Documents
# ==================================================================
elif page == "Documents":
    st.markdown('<p class="main-header">Documents</p>', unsafe_allow_html=True)
    if not subject_id:
        st.warning("Select a subject in the sidebar first.")
        st.stop()
    st.markdown(f'<p class="sub-header">Documents for: <b>{subject_names.get(subject_id)}</b></p>', unsafe_allow_html=True)

    docs_resp = requests.get(f"{API_BASE}/subjects/{subject_id}/documents", headers=auth_headers())
    docs = docs_resp.json() if docs_resp.status_code == 200 else []

    type_filter = st.selectbox("Filter by type", ["All"] + list(set(d["document_type"] for d in docs)))
    filtered = docs if type_filter == "All" else [d for d in docs if d["document_type"] == type_filter]

    if filtered:
        for d in filtered:
            col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
            with col1:
                st.write(f"📄 {d['file_name']}")
            with col2:
                badge_class = "badge-purple" if d["document_type"] == "syllabus" else "badge"
                st.markdown(f'<span class="badge {badge_class}">{d["document_type"]}</span>', unsafe_allow_html=True)
            with col3:
                st.caption(d["created_at"][:10])
            with col4:
                if st.button("🗑️", key=f"del_doc_{d['id']}"):
                    resp = requests.delete(
                        f"{API_BASE}/subjects/{subject_id}/documents/{d['id']}",
                        headers=auth_headers(),
                    )
                    if resp.status_code == 200:
                        st.success("Deleted.")
                        st.rerun()
                    else:
                        st.error(resp.text)
    else:
        st.info("No documents yet — go to the Upload tab.")
# ==================================================================
# PAGE: Upload
# ==================================================================
elif page == "Upload":
    st.markdown('<p class="main-header">Upload Documents</p>', unsafe_allow_html=True)
    if not subject_id:
        st.warning("Select a subject in the sidebar first.")
        st.stop()
    st.markdown(f'<p class="sub-header">Uploading for: <b>{subject_names.get(subject_id)}</b></p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Syllabus**")
        syllabus_file = st.file_uploader("Upload syllabus PDF", type="pdf", key="syllabus_uploader")
        if syllabus_file and st.button("Upload Syllabus"):
            files = {"file": (syllabus_file.name, syllabus_file.getvalue(), "application/pdf")}
            data = {"document_type": "syllabus"}
            resp = requests.post(f"{API_BASE}/subjects/{subject_id}/documents", files=files, data=data, headers=auth_headers())
            st.success("Uploaded!") if resp.status_code == 200 else st.error(resp.text)

    with col2:
        st.markdown("**Study Material**")
        study_file = st.file_uploader("Upload study material PDF", type="pdf", key="study_uploader")
        if study_file and st.button("Upload Study Material"):
            files = {"file": (study_file.name, study_file.getvalue(), "application/pdf")}
            data = {"document_type": "study_material"}
            resp = requests.post(f"{API_BASE}/subjects/{subject_id}/documents", files=files, data=data, headers=auth_headers())
            st.success("Uploaded!") if resp.status_code == 200 else st.error(resp.text)

    with col3:
        st.markdown("**Previous Year Questions**")
        pyq_files = st.file_uploader(
            "Upload PYQ PDFs (one or more)", type="pdf", key="pyq_uploader", accept_multiple_files=True
        )
        if pyq_files and st.button("Upload PYQs"):
            success_count = 0
            for f in pyq_files:
                files = {"file": (f.name, f.getvalue(), "application/pdf")}
                data = {"document_type": "previous_year_question"}
                resp = requests.post(f"{API_BASE}/subjects/{subject_id}/documents", files=files, data=data, headers=auth_headers())
                if resp.status_code == 200:
                    success_count += 1
            st.success(f"Uploaded {success_count}/{len(pyq_files)} PYQ files")

# ==================================================================
# PAGE: Question Generation
# ==================================================================
elif page == "Question Generation":
    st.markdown('<p class="main-header">AI Question Generation Engine</p>', unsafe_allow_html=True)
    if not subject_id:
        st.warning("Select a subject in the sidebar first.")
        st.stop()
    st.markdown(f'<p class="sub-header">Run the analysis pipeline for: <b>{subject_names.get(subject_id)}</b></p>', unsafe_allow_html=True)

    kb_status_resp = requests.get(f"{API_BASE}/subjects/{subject_id}/knowledge-base-status", headers=auth_headers())
    if kb_status_resp.status_code == 200 and kb_status_resp.json().get("exists"):
        st.success("✅ Knowledge base already built for this subject — you can skip straight to 'Generate Final Questions' below, or re-run steps if you've updated documents.")
    steps = [
        ("1. Analyze Syllabus", f"/subjects/{subject_id}/analyze-syllabus"),
        ("2. Extract PYQs", f"/subjects/{subject_id}/extract-pyqs"),
        ("3. Classify Topics", f"/subjects/{subject_id}/classify-topics"),
        ("4. Map Concepts", f"/subjects/{subject_id}/map-concepts"),
        ("5. Analyze Repetition", f"/subjects/{subject_id}/analyze-repetition"),
        ("6. Analyze Patterns", f"/subjects/{subject_id}/analyze-patterns"),
        ("7. Build Knowledge Base", f"/subjects/{subject_id}/build-knowledge-base"),
    ]

    step_status_key = f"step_status_{subject_id}"
    if step_status_key not in st.session_state:
        st.session_state[step_status_key] = {}

    cols = st.columns(len(steps))
    for i, (label, endpoint) in enumerate(steps):
        with cols[i]:
            st.markdown(f"**{label}**")
            if st.button("Run", key=f"run_{endpoint}", use_container_width=True):
                with st.spinner("Running..."):
                    resp = requests.post(f"{API_BASE}{endpoint}", headers=auth_headers())
                if resp.status_code == 200:
                    st.session_state[step_status_key][endpoint] = True
                    st.rerun()
                else:
                    st.session_state[step_status_key][endpoint] = False
                    st.error(resp.text)

            if st.session_state[step_status_key].get(endpoint) is True:
                st.markdown('<div style="text-align:center; color:#059669; font-size:1.3rem;">✅</div>', unsafe_allow_html=True)
            elif st.session_state[step_status_key].get(endpoint) is False:
                st.markdown('<div style="text-align:center; color:#dc2626; font-size:1.3rem;">❌</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("Generate Questions")
    col1, col2, col3 = st.columns(3)
    with col1:
        num_topics = st.number_input("Number of top topics", min_value=1, max_value=29, value=8)
    with col2:
        questions_per_topic = st.number_input("Questions per topic", min_value=1, max_value=10, value=4)
    with col3:
        final_top_n = st.number_input("Final question count", min_value=5, max_value=50, value=20)

    if st.button("⚡ Generate Final Questions", type="primary"):
        with st.spinner("Generating questions... this may take 1-2 minutes"):
            resp = requests.post(
                f"{API_BASE}/subjects/{subject_id}/generate-questions",
                params={
                    "num_topics": num_topics,
                    "questions_per_topic": questions_per_topic,
                    "final_top_n": final_top_n,
                },
                headers=auth_headers(),
            )
        if resp.status_code == 200:
            result = resp.json()
            st.success(f"Generated {result.get('total_generated', 0)} candidates → {result.get('final_top_n', 0)} ranked questions.")
        else:
            st.error(f"Generation failed: {resp.text}")

# ==================================================================
# PAGE: Ask Question
# ==================================================================
elif page == "Ask Question":
    st.markdown('<p class="main-header">Ask a Question</p>', unsafe_allow_html=True)
    if not subject_id:
        st.warning("Select a subject in the sidebar first.")
        st.stop()
    st.markdown(f'<p class="sub-header">Ask anything about: <b>{subject_names.get(subject_id)}</b> — answers are grounded in your uploaded study material and syllabus.</p>', unsafe_allow_html=True)

    chat_key = f"chat_history_{subject_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("Sources"):
                    for s in msg["sources"]:
                        st.caption(f"• {s}")

    user_question = st.chat_input("Ask a question about this subject...")
    if user_question:
        st.session_state[chat_key].append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                resp = requests.post(
                    f"{API_BASE}/subjects/{subject_id}/ask",
                    json={"question": user_question},
                    headers=auth_headers(),
                )
            if resp.status_code == 200:
                data = resp.json()
                st.markdown(data["answer"])
                if data.get("sources"):
                    with st.expander("Sources"):
                        for s in data["sources"]:
                            st.caption(f"• {s}")
                st.session_state[chat_key].append({
                    "role": "assistant",
                    "content": data["answer"],
                    "sources": data.get("sources", []),
                })
            else:
                error_msg = resp.json().get("detail", "Something went wrong") if resp.headers.get("content-type", "").startswith("application/json") else resp.text
                st.error(error_msg)
                st.session_state[chat_key].append({"role": "assistant", "content": f"Error: {error_msg}"})

# ==================================================================
# PAGE: Results
# ==================================================================
elif page == "Results":
    st.markdown('<p class="main-header">Results</p>', unsafe_allow_html=True)
    if not subject_id:
        st.warning("Select a subject in the sidebar first.")
        st.stop()
    st.markdown(f'<p class="sub-header">Generated question bank for: <b>{subject_names.get(subject_id)}</b></p>', unsafe_allow_html=True)

    st.info(
        "ℹ️ These questions are newly generated based on historical patterns and syllabus content. "
        "They are **not** questions that will definitely appear in any future exam — the evidence score "
        "reflects how strongly a *topic* has recurred historically, not a prediction for this specific question."
    )

    final_resp = requests.get(f"{API_BASE}/subjects/{subject_id}/final-questions", headers=auth_headers())
    final_questions = final_resp.json() if final_resp.status_code == 200 else []

    patterns_resp = requests.get(f"{API_BASE}/subjects/{subject_id}/patterns", headers=auth_headers())
    patterns = patterns_resp.json() if patterns_resp.status_code == 200 else []

    if not final_questions:
        st.info("No generated questions yet — run 'Generate Final Questions' in the Question Generation tab.")
        st.stop()

    # ---- Stat cards ----
    all_years = sorted(set(y for p in patterns for y in p["years"]))
    unique_topics = len(set(q["topic_name"] for q in final_questions))
    avg_score = round(sum(q["evidence_score"] for q in final_questions) / len(final_questions), 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">📄 Total Questions</div>
        <div class="stat-value">{len(final_questions)}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">🧩 Unique Topics</div>
        <div class="stat-value">{unique_topics}</div></div>""", unsafe_allow_html=True)
    with c3:
        year_range = f"{min(all_years)} – {max(all_years)}" if all_years else "—"
        st.markdown(f"""<div class="stat-card"><div class="stat-label">📅 Years Analyzed</div>
        <div class="stat-value" style="font-size:1.3rem;">{year_range}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">📊 Avg Evidence Score</div>
        <div class="stat-value">{avg_score}<span style="font-size:1rem;">/100</span></div></div>""", unsafe_allow_html=True)

    st.divider()

    col_left, col_right = st.columns([2, 1])

    # ---- Historical Pattern table ----
    with col_left:
        st.subheader("Historical Pattern Analysis")
        if patterns:
            table_data = [
                {
                    "Topic": p["topic_name"],
                    "Category": p["unit_name"],
                    "Appearances": f"{p['frequency']}/{p['total_papers']}",
                    "Years": ", ".join(str(y) for y in p["years"]),
                }
                for p in patterns[:10]
            ]
            st.dataframe(table_data, use_container_width=True, hide_index=True)

    # ---- Donut chart ----
    with col_right:
        st.subheader("Topic Distribution")
        topic_counts = {}
        for q in final_questions:
            topic_counts[q["topic_name"]] = topic_counts.get(q["topic_name"], 0) + 1

        fig = go.Figure(data=[go.Pie(
            labels=list(topic_counts.keys()),
            values=list(topic_counts.values()),
            hole=0.6,
            marker=dict(colors=["#7c3aed", "#a78bfa", "#f472b6", "#fb923c", "#34d399", "#60a5fa", "#fbbf24", "#f87171"]),
        )])
        fig.update_layout(
            showlegend=True,
            margin=dict(t=0, b=0, l=0, r=0),
            height=280,
            annotations=[dict(text=f"{unique_topics}<br>Topics", x=0.5, y=0.5, font_size=16, showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---- Final questions + PDF download ----
    st.subheader("Final Ranked Questions")

    pdf_resp = requests.get(f"{API_BASE}/subjects/{subject_id}/final-questions/pdf", headers=auth_headers())
    if pdf_resp.status_code == 200:
        st.download_button(
            label="📄 Download All (PDF)",
            data=pdf_resp.content,
            file_name=f"{subject_names.get(subject_id, 'subject')}_question_bank.pdf",
            mime="application/pdf",
            type="primary",
        )
    else:
        st.warning(f"PDF not available yet ({pdf_resp.status_code}): {pdf_resp.text}")

    for i, q in enumerate(final_questions, start=1):
        col1, col2 = st.columns([5, 1])
        with col1:
            with st.expander(f"Q{i}. [{q['topic_name']}] {q['question_text'][:80]}..."):
                st.markdown(f"**Full question:** {q['question_text']}")
                st.write(f"**Marks:** {q['marks']} | **Difficulty:** {q['difficulty']} | **Type:** {q['question_type']}")
                st.write(f"**Why this question?** {q['generation_reason']}")
                st.write(f"**Supporting years:** {q['supporting_years']}")
                if q.get("evidence_breakdown"):
                    st.write("**Score breakdown:**")
                    st.json(q["evidence_breakdown"])
        with col2:
            st.markdown(f'<span class="badge">Evidence: {q["evidence_score"]}</span>', unsafe_allow_html=True)