"""Creates your private .env file by asking you 5 questions.
Run it with:  py make_env.py
"""

print()
print("Type each answer, then press Enter.")
print("Tip: right-click in this window to paste.")
print()

host = input("1) Host (Connectivity tab on FalkorDB Cloud): ").strip()
port = input("2) Port (a number, Connectivity tab): ").strip()
user = input("3) Username (just press Enter to use: falkordb): ").strip() or "falkordb"
password = input("4) Password (Instance Details tab): ").strip()
gemini = input("5) Gemini API key (press Enter to skip for now): ").strip()

# Clean common copy-paste mistakes
for prefix in ("https://", "http://", "redis://", "rediss://"):
    if host.startswith(prefix):
        host = host[len(prefix):]
host = host.rstrip("/")
if ":" in host:
    host, maybe_port = host.rsplit(":", 1)
    if maybe_port.isdigit() and not port:
        port = maybe_port

if not host or not port or not password:
    print()
    print("Host, port and password cannot be empty. Run this again.")
    raise SystemExit(1)

with open(".env", "w", encoding="utf-8") as f:
    f.write(f"FALKORDB_HOST={host}\n")
    f.write(f"FALKORDB_PORT={port}\n")
    f.write(f"FALKORDB_USERNAME={user}\n")
    f.write(f"FALKORDB_PASSWORD={password}\n")
    f.write(f"GEMINI_API_KEY={gemini}\n")

print()
print("Done. Your .env file was saved in this folder.")
print("Next step: run   py test_connection.py")
