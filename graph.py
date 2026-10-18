"""All FalkorDB work for Campus Brain: seeding, planning (multi-hop
prerequisite queries), and per-student memory."""

import os
import re
import time

from dotenv import load_dotenv
from falkordb import FalkorDB

from data import PREREQS, QUESTIONS, TOPICS

load_dotenv()
CURRICULUM = "curriculum"

# ---------------------------------------------------------------- queries
# Every prerequisite of the target, with the LONGEST path length (depth).
# Larger depth = more foundational = study it earlier.
Q_PREREQ_DEPTH = """
MATCH p=(a:Topic)-[:PREREQUISITE_OF*1..8]->(t:Topic {name:$target})
RETURN a.name, a.unit, max(length(p))
"""

# The actual chains, used to explain WHY each topic is in the plan.
Q_CHAINS = """
MATCH p=(a:Topic)-[:PREREQUISITE_OF*1..8]->(t:Topic {name:$target})
RETURN a.name, [n IN nodes(p) | n.name]
"""

# How many (synthetic) exam questions test each topic.
Q_QCOUNT = """
MATCH (q:Question)-[:TESTS]->(t:Topic)
WHERE t.name IN $names
RETURN t.name, count(q)
"""

# Memory, in the per-student graph.
Q_MASTERED = "MATCH (:Student)-[:MASTERED]->(t:Topic) RETURN t.name"
Q_SAVE_MASTERED = """
MATCH (s:Student {name:$s})
MERGE (t:Topic {name:$t})
MERGE (s)-[r:MASTERED]->(t)
SET r.at = $ts
"""
Q_SAVE_SESSION = """
MATCH (s:Student {name:$s})
CREATE (s)-[:HAD_SESSION]->(:Session {goal:$g, at:$ts, learned:$n})
"""
Q_HISTORY = """
MATCH (:Student)-[:HAD_SESSION]->(x:Session)
RETURN x.goal, x.at, x.learned
ORDER BY x.at DESC LIMIT 5
"""


# ------------------------------------------------------------- connection
def _secret(name, default=None):
    """Read from Streamlit secrets (when deployed) or from .env / env vars."""
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.environ.get(name, default)


def connect():
    return FalkorDB(
        host=_secret("FALKORDB_HOST"),
        port=int(_secret("FALKORDB_PORT", "6379")),
        username=_secret("FALKORDB_USERNAME") or None,
        password=_secret("FALKORDB_PASSWORD") or None,
    )


def student_graph_name(student):
    slug = re.sub(r"[^a-z0-9]+", "_", student.lower()).strip("_") or "demo"
    return "student_" + slug


# ---------------------------------------------------------------- seeding
def is_seeded(db):
    try:
        r = db.select_graph(CURRICULUM).query("MATCH (t:Topic) RETURN count(t)")
        return r.result_set[0][0] > 0
    except Exception:
        return False


def seed_curriculum(db):
    try:
        db.select_graph(CURRICULUM).delete()
    except Exception:
        pass
    g = db.select_graph(CURRICULUM)
    for name, unit in TOPICS:
        g.query("CREATE (:Topic {name:$n, unit:$u})", {"n": name, "u": unit})
    try:
        g.query("CREATE INDEX FOR (t:Topic) ON (t.name)")
    except Exception:
        pass
    for topic, pres in PREREQS.items():
        g.query(
            "MATCH (b:Topic {name:$b}) WITH b UNWIND $pres AS p "
            "MATCH (a:Topic {name:p}) CREATE (a)-[:PREREQUISITE_OF]->(b)",
            {"b": topic, "pres": pres},
        )
    for text, marks, year, topics in QUESTIONS:
        g.query(
            "CREATE (q:Question {text:$t, marks:$m, year:$y}) WITH q "
            "UNWIND $names AS n MATCH (t:Topic {name:n}) CREATE (q)-[:TESTS]->(t)",
            {"t": text, "m": marks, "y": year, "names": topics},
        )


def all_topics(db):
    r = db.select_graph(CURRICULUM).query("MATCH (t:Topic) RETURN t.name, t.unit ORDER BY t.unit, t.name")
    return [(row[0], row[1]) for row in r.result_set]


# --------------------------------------------------------------- planning
def mastered_topics(db, student):
    try:
        sg = db.select_graph(student_graph_name(student))
        return {row[0] for row in sg.query(Q_MASTERED).result_set}
    except Exception:
        return set()


def build_plan(db, student, target):
    """Return (steps, known) for the target. Each step is a dict."""
    cur = db.select_graph(CURRICULUM)
    mastered = mastered_topics(db, student)

    rows = cur.query(Q_PREREQ_DEPTH, {"target": target}).result_set
    info = {name: {"unit": unit, "depth": depth} for name, unit, depth in rows}

    chains = {}
    for name, chain in cur.query(Q_CHAINS, {"target": target}).result_set:
        if name not in chains or len(chain) < len(chains[name]):
            chains[name] = chain

    unit_row = cur.query("MATCH (t:Topic {name:$t}) RETURN t.unit", {"t": target}).result_set
    info[target] = {"unit": unit_row[0][0] if unit_row else "", "depth": 0}
    chains[target] = [target]

    counts = {n: c for n, c in cur.query(Q_QCOUNT, {"names": list(info)}).result_set}

    steps = []
    for name, d in info.items():
        steps.append(
            {
                "topic": name,
                "unit": d["unit"],
                "depth": d["depth"],
                "questions": counts.get(name, 0),
                "chain": " → ".join(chains.get(name, [name])),
                "known": name in mastered,
            }
        )
    pending = [s for s in steps if not s["known"]]
    known = [s for s in steps if s["known"]]
    pending.sort(key=lambda s: (-s["depth"], -s["questions"], s["topic"]))
    return pending, known


# ----------------------------------------------------------------- memory
def save_progress(db, student, topics, goal):
    sg = db.select_graph(student_graph_name(student))
    ts = int(time.time())
    sg.query("MERGE (:Student {name:$s})", {"s": student})
    for t in topics:
        sg.query(Q_SAVE_MASTERED, {"s": student, "t": t, "ts": ts})
    sg.query(Q_SAVE_SESSION, {"s": student, "g": goal, "ts": ts, "n": len(topics)})


def history(db, student):
    try:
        sg = db.select_graph(student_graph_name(student))
        return sg.query(Q_HISTORY).result_set
    except Exception:
        return []


def reset_student(db, student):
    try:
        db.select_graph(student_graph_name(student)).delete()
    except Exception:
        pass


# ------------------------------------------------------------ optional AI
def coach_text(student, target, pending, known):
    """Gemini only RE-WORDS what the graph returned. No key -> returns None."""
    key = _secret("GEMINI_API_KEY")
    if not key:
        return None
    try:
        from google import genai

        client = genai.Client(api_key=key)
        facts = "\n".join(
            f"{i + 1}. {s['topic']} (path: {s['chain']}; tested by {s['questions']} past questions)"
            for i, s in enumerate(pending)
        )
        prompt = (
            f"You are a friendly study coach. Student {student} wants to learn '{target}'. "
            f"Already known: {', '.join(s['topic'] for s in known) or 'nothing yet'}.\n"
            "Using ONLY the ordered plan below (it came from a knowledge graph), write a short, "
            "motivating explanation of why this order makes sense. Do not add topics.\n" + facts
        )
        model = _secret("GEMINI_MODEL", "gemini-2.5-flash")
        return client.models.generate_content(model=model, contents=prompt).text
    except Exception as e:
        return f"(Gemini explanation unavailable: {e})"
