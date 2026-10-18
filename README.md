# Campus Brain

A graph-powered study agent for Data Structures, built for **Graph Hacks: Context for AI Agents** (FalkorDB x WeMakeDevs).

**Tracks entered:** Agents That Act on Connected Data, and Agent Memory and Coordination.

- Live demo: ADD-YOUR-STREAMLIT-LINK-HERE
- Demo video: ADD-YOUR-VIDEO-LINK-HERE

## The problem
Students don't know what to study first. Topics depend on each other (you cannot learn AVL trees before BSTs, or BSTs before trees), but a plain chatbot cannot see those dependencies or remember what a student already knows.

## What it does
1. You pick a goal topic, for example "AVL Trees".
2. The agent walks the prerequisite graph with multi-hop Cypher queries and builds an ordered study plan.
3. Every step shows its **path through the graph**, so you can see why it is there, plus how many past exam questions test it.
4. You mark topics as studied. The agent writes that to a **private memory graph for that student**, and the next plan shrinks.

If FalkorDB is removed, no plan can be produced. The graph does the work.

## Data model
**Graph `curriculum` (shared)**
- `(:Topic {name, unit})`
- `(:Question {text, marks, year})` (synthetic)
- `(:Topic)-[:PREREQUISITE_OF]->(:Topic)`
- `(:Question)-[:TESTS]->(:Topic)`

**Graph `student_<name>` (one per student, private memory)**
- `(:Student {name})`
- `(:Topic {name})`
- `(:Session {goal, at, learned})`
- `(:Student)-[:MASTERED {at}]->(:Topic)`
- `(:Student)-[:HAD_SESSION]->(:Session)`

## Cypher queries the product depends on
See `graph.py` (also shown inside the app under "How it works"):
- `Q_PREREQ_DEPTH`: all transitive prerequisites with the longest path length (variable-length path + aggregation). Deeper means more foundational, so it comes earlier.
- `Q_CHAINS`: the actual path of topic names, used to explain each step.
- `Q_QCOUNT`: exam questions testing each topic.
- `Q_SAVE_MASTERED`, `Q_SAVE_SESSION`, `Q_MASTERED`, `Q_HISTORY`: episodic and semantic memory in the student's own graph.

## Agent coordination
The planner reads the curriculum graph and the student's graph, and writes the plan. The student's progress is written back to the student graph, and the next plan is built from that updated state. The optional Gemini step only rewords what the graph returned.

## Run it yourself
1. Create a free FalkorDB Cloud instance and note its host, port, username and password.
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in the values (GEMINI_API_KEY is optional).
4. `py test_connection.py` to check the connection.
5. `py -m streamlit run app.py`

The curriculum graph seeds itself on first run, so a fresh or expired free-tier instance rebuilds automatically.

## Data
All data is public or synthetic. Topics follow a typical Data Structures syllabus. Exam questions were written for this project. No personal or private data is used.

## AI use disclosure
- I used AI coding assistants (Gemini and Claude) during development, for code drafts, debugging and explanations.
- I ran, debugged and adapted the code myself and can explain the graph model, the queries and the architecture.
- At runtime, Gemini (optional) only rewords the plan that FalkorDB returns.

## Built by
ADD-YOUR-NAME, B.Tech CSE, BPIT, Delhi.
