import streamlit as st

import graph as G

st.set_page_config(page_title="Campus Brain", page_icon="🧠", layout="wide")
st.title("🧠 Campus Brain")
st.caption("A graph-powered study agent for Data Structures. The plan, the memory and the explanations all come from FalkorDB.")


@st.cache_resource
def get_db():
    return G.connect()


try:
    db = get_db()
    if not G.is_seeded(db):
        with st.spinner("Building the curriculum graph (first run only, ~20 seconds)..."):
            G.seed_curriculum(db)
except Exception as e:
    st.error(f"Could not connect to FalkorDB: {e}")
    st.stop()

# ---------------------------------------------------------------- sidebar
st.sidebar.header("Student")
student = st.sidebar.text_input("Your name", "demo").strip() or "demo"
topics = G.all_topics(db)
names = [t[0] for t in topics]
default = names.index("AVL Trees") if "AVL Trees" in names else 0
target = st.sidebar.selectbox("What do you want to learn or revise?", names, index=default)
if st.sidebar.button("Re-seed curriculum graph"):
    with st.spinner("Rebuilding..."):
        G.seed_curriculum(db)
    st.rerun()
if st.sidebar.button("Reset my memory"):
    G.reset_student(db, student)
    st.rerun()

# ------------------------------------------------------------------- plan
pending, known = G.build_plan(db, student, target)

left, right = st.columns([2, 1])

with left:
    st.subheader(f"Study plan for: {target}")
    a, b, c = st.columns(3)
    a.metric("Steps left", len(pending))
    b.metric("Already known (memory)", len(known))
    c.metric("Questions covered", sum(s["questions"] for s in pending))

    if pending:
        rows = [
            {
                "Step": i + 1,
                "Topic": s["topic"],
                "Unit": s["unit"],
                "Why (path through the graph)": s["chain"],
                "Past questions": s["questions"],
            }
            for i, s in enumerate(pending)
        ]
        st.dataframe(rows, width="stretch", hide_index=True)

        st.markdown("**Finished some steps? Tell the agent and it will remember.**")
        done = st.multiselect("Topics I have now studied", [s["topic"] for s in pending])
        if st.button("Save my progress", type="primary", disabled=not done):
            G.save_progress(db, student, done, target)
            st.success("Saved to your private memory graph. Your plan will now change.")
            st.rerun()

        if st.button("Explain my plan (Gemini)"):
            text = G.coach_text(student, target, pending, known)
            st.info(text or "Add GEMINI_API_KEY to enable this. The plan above works without it.")
    else:
        st.success(f"You have covered everything needed for {target}. Pick a new goal in the sidebar.")

with right:
    st.subheader("What the agent remembers")
    st.caption(f"Private graph: {G.student_graph_name(student)}")
    if known:
        for s in known:
            st.markdown(f"✅ {s['topic']}")
    else:
        st.write("Nothing yet. Mark some topics as studied.")
    st.markdown("**Recent sessions**")
    hist = G.history(db, student)
    if hist:
        for goal, ts, n in hist:
            st.write(f"• goal **{goal}**, learned {n} topic(s)")
    else:
        st.write("No sessions yet.")

with st.expander("How it works: the graph queries behind this page"):
    st.markdown("Curriculum graph: `Topic` nodes joined by `PREREQUISITE_OF`, and `Question` nodes joined by `TESTS`. One private graph per student holds `MASTERED` and `HAD_SESSION` memory.")
    st.code(G.Q_PREREQ_DEPTH, language="cypher")
    st.code(G.Q_CHAINS, language="cypher")
    st.code(G.Q_QCOUNT, language="cypher")
    st.code(G.Q_SAVE_MASTERED, language="cypher")
