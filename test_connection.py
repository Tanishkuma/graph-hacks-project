import os
import sys

from dotenv import load_dotenv

load_dotenv()

missing = [n for n in ("FALKORDB_HOST", "FALKORDB_PORT", "FALKORDB_PASSWORD") if not os.environ.get(n)]
if missing:
    print("Your .env file is missing:", ", ".join(missing))
    print("Fix: run   py make_env.py")
    sys.exit(1)

from falkordb import FalkorDB

try:
    db = FalkorDB(
        host=os.environ["FALKORDB_HOST"],
        port=int(os.environ["FALKORDB_PORT"]),
        username=os.environ.get("FALKORDB_USERNAME") or None,
        password=os.environ["FALKORDB_PASSWORD"],
    )
    g = db.select_graph("connection_test")
    g.query("CREATE (:Topic {name:'Arrays'})-[:PREREQUISITE_OF]->(:Topic {name:'Linked Lists'})")
    result = g.query("MATCH (a:Topic)-[:PREREQUISITE_OF]->(b:Topic) RETURN a.name, b.name")
    print(result.result_set)
    g.delete()
    print()
    print("Connection works. You are ready for the next step.")
except Exception as e:
    msg = str(e)
    print()
    print("CONNECTION FAILED.")
    if "username-password" in msg or "WRONGPASS" in msg:
        print("Reason: wrong username or password.")
        print("Fix: username must be  falkordb  (unless you made another user).")
        print("     Copy the password again from the Instance Details tab, then run: py make_env.py")
    elif "getaddrinfo" in msg or "Name or service" in msg:
        print("Reason: the host name was not found.")
        print("Fix: check the instance says Running, and copy the host again from the Connectivity tab.")
    elif "imeout" in msg or "refused" in msg:
        print("Reason: the server did not answer.")
        print("Fix: wait 3 minutes for the instance to say Running, check the port number, try again.")
    else:
        print("Reason: something else. Copy the line below and send it to Claude:")
    print()
    print("Technical message:", msg)
    sys.exit(1)
