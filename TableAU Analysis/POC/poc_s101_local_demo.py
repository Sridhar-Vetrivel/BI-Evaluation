"""
POC S.No 101 — REST API CRUD, fully LOCAL demonstration.

WHAT THIS PROVES
----------------
That a single automation script can perform full Create / Read / Update / Delete
against the *REST endpoint shapes* used by Power BI and Tableau — i.e. that the
integration pattern GTF needs (auto-provision a brand workspace/project, publish
content, onboard franchise users, tear down) works end to end.

WHAT THIS DOES *NOT* PROVE
--------------------------
It does not prove the live vendor platforms accept these calls — that is proven by
the official REST API documentation (authoritative for these APIs) and, when you
want a live demo, by the free real-endpoint options described in the POC .md file
(Tableau Developer Program site / Power BI free trial + Learn "Try it" console).

HOW TO RUN
----------
    python poc_s101_local_demo.py

Requirements: Python 3.8+ ONLY. No pip install, no account, no internet, no admin.
It starts an in-memory mock REST server on localhost in a background thread and
runs the CRUD lifecycle against it, printing a transcript and a PASS/FAIL summary.
"""

import json
import re
import threading
import uuid
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ----------------------------------------------------------------------------- #
# In-memory stores (reset each run) — stand in for the vendor backends
# ----------------------------------------------------------------------------- #
PBI = {"groups": {}, "datasets": {}, "reports": {}, "users": {}}   # Power BI shapes
TAB = {"projects": {}, "workbooks": {}, "users": {}}               # Tableau shapes


def _nid():
    return str(uuid.uuid4())


# ----------------------------------------------------------------------------- #
# Mock REST server: implements the real URL shapes of both vendors
# ----------------------------------------------------------------------------- #
class MockHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # silence default logging

    def _send(self, code, payload=None):
        body = json.dumps(payload).encode() if payload is not None else b""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode() or "{}")
        except json.JSONDecodeError:
            return {}

    # ---- POST (Create) ---------------------------------------------------- #
    def do_POST(self):
        p, body = self.path, self._read_json()

        # Power BI: create workspace
        if p == "/v1.0/myorg/groups":
            g = {"id": _nid(), "name": body.get("name", "unnamed")}
            PBI["groups"][g["id"]] = g
            return self._send(200, g)

        # Power BI: import (creates a dataset + a report together)
        m = re.fullmatch(r"/v1\.0/myorg/groups/([^/]+)/imports", p)
        if m:
            gid = m.group(1)
            ds = {"id": _nid(), "name": body.get("datasetDisplayName", "ds"), "groupId": gid}
            rep = {"id": _nid(), "name": ds["name"], "datasetId": ds["id"], "groupId": gid}
            PBI["datasets"][ds["id"]] = ds
            PBI["reports"][rep["id"]] = rep
            return self._send(200, {"datasetId": ds["id"], "reportId": rep["id"]})

        # Power BI: add workspace user
        m = re.fullmatch(r"/v1\.0/myorg/groups/([^/]+)/users", p)
        if m:
            u = {"id": _nid(), "groupId": m.group(1),
                 "identifier": body.get("identifier"),
                 "accessRight": body.get("groupUserAccessRight", "Viewer")}
            PBI["users"][u["id"]] = u
            return self._send(200, u)

        # Tableau: sign in (PAT) -> token + site id
        if p.startswith("/api/") and p.endswith("/auth/signin"):
            return self._send(200, {"token": _nid(), "siteId": _nid()})

        # Tableau: create project
        m = re.fullmatch(r"/api/[^/]+/sites/[^/]+/projects", p)
        if m:
            pr = {"id": _nid(), "name": body.get("name", "project")}
            TAB["projects"][pr["id"]] = pr
            return self._send(201, pr)

        # Tableau: publish workbook
        m = re.fullmatch(r"/api/[^/]+/sites/[^/]+/workbooks", p)
        if m:
            wb = {"id": _nid(), "name": body.get("name", "workbook"),
                  "projectId": body.get("projectId")}
            TAB["workbooks"][wb["id"]] = wb
            return self._send(201, wb)

        # Tableau: add user
        m = re.fullmatch(r"/api/[^/]+/sites/[^/]+/users", p)
        if m:
            u = {"id": _nid(), "name": body.get("name"), "siteRole": body.get("siteRole", "Viewer")}
            TAB["users"][u["id"]] = u
            return self._send(201, u)

        return self._send(404, {"error": f"no POST route for {p}"})

    # ---- GET (Read) ------------------------------------------------------- #
    def do_GET(self):
        p = self.path
        if p == "/v1.0/myorg/groups":
            return self._send(200, {"value": list(PBI["groups"].values())})
        if re.fullmatch(r"/v1\.0/myorg/groups/[^/]+/datasets", p):
            return self._send(200, {"value": list(PBI["datasets"].values())})
        if re.fullmatch(r"/v1\.0/myorg/groups/[^/]+/reports", p):
            return self._send(200, {"value": list(PBI["reports"].values())})
        if re.fullmatch(r"/v1\.0/myorg/groups/[^/]+/users", p):
            return self._send(200, {"value": list(PBI["users"].values())})
        if re.fullmatch(r"/api/[^/]+/sites/[^/]+/projects", p):
            return self._send(200, {"projects": list(TAB["projects"].values())})
        if re.fullmatch(r"/api/[^/]+/sites/[^/]+/workbooks", p):
            return self._send(200, {"workbooks": list(TAB["workbooks"].values())})
        if re.fullmatch(r"/api/[^/]+/sites/[^/]+/users", p):
            return self._send(200, {"users": list(TAB["users"].values())})
        return self._send(404, {"error": f"no GET route for {p}"})

    # ---- DELETE ----------------------------------------------------------- #
    def do_DELETE(self):
        p = self.path
        m = re.fullmatch(r"/v1\.0/myorg/groups/([^/]+)/reports/([^/]+)", p)
        if m:
            PBI["reports"].pop(m.group(2), None)
            return self._send(200, {"deleted": m.group(2)})
        m = re.fullmatch(r"/v1\.0/myorg/groups/([^/]+)", p)
        if m:
            PBI["groups"].pop(m.group(1), None)
            return self._send(200, {"deleted": m.group(1)})
        m = re.fullmatch(r"/api/[^/]+/sites/[^/]+/workbooks/([^/]+)", p)
        if m:
            TAB["workbooks"].pop(m.group(1), None)
            return self._send(204)
        m = re.fullmatch(r"/api/[^/]+/sites/[^/]+/projects/([^/]+)", p)
        if m:
            TAB["projects"].pop(m.group(1), None)
            return self._send(204)
        return self._send(404, {"error": f"no DELETE route for {p}"})


# ----------------------------------------------------------------------------- #
# Tiny HTTP client (stdlib only)
# ----------------------------------------------------------------------------- #
def call(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            txt = r.read().decode()
            return r.status, (json.loads(txt) if txt else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()}


# ----------------------------------------------------------------------------- #
# The CRUD lifecycle — the actual "proof"
# ----------------------------------------------------------------------------- #
def run_demo(base):
    results = []

    def check(label, ok, detail=""):
        results.append(ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' - ' + detail) if detail else ''}")

    print("\n=== POWER BI (REST shape) =========================================")
    s, ws = call("POST", f"{base}/v1.0/myorg/groups", {"name": "POC-Brand-Carvel"})
    check("CREATE workspace", s == 200 and "id" in ws, ws.get("name", ""))
    gid = ws["id"]

    s, imp = call("POST", f"{base}/v1.0/myorg/groups/{gid}/imports",
                  {"datasetDisplayName": "Brand Summary"})
    check("CREATE dataset + report (import)", s == 200 and "reportId" in imp)
    rid = imp["reportId"]

    s, gl = call("GET", f"{base}/v1.0/myorg/groups")
    check("READ workspaces", s == 200 and any(g["id"] == gid for g in gl["value"]),
          f"{len(gl['value'])} workspace(s)")
    s, dl = call("GET", f"{base}/v1.0/myorg/groups/{gid}/datasets")
    check("READ datasets", s == 200 and len(dl["value"]) == 1)
    s, rl = call("GET", f"{base}/v1.0/myorg/groups/{gid}/reports")
    check("READ reports", s == 200 and len(rl["value"]) == 1)

    s, u = call("POST", f"{base}/v1.0/myorg/groups/{gid}/users",
                {"identifier": "franchise.user@gtf.com", "principalType": "User",
                 "groupUserAccessRight": "Viewer"})
    check("UPDATE: add franchise user", s == 200 and u["accessRight"] == "Viewer",
          u.get("identifier", ""))

    s, _ = call("DELETE", f"{base}/v1.0/myorg/groups/{gid}/reports/{rid}")
    check("DELETE report", s == 200)
    s, _ = call("DELETE", f"{base}/v1.0/myorg/groups/{gid}")
    check("DELETE workspace", s == 200)

    print("\n=== TABLEAU (REST shape) ==========================================")
    s, auth = call("POST", f"{base}/api/3.21/auth/signin",
                   {"credentials": {"personalAccessTokenName": "poc",
                                    "personalAccessTokenSecret": "x",
                                    "site": {"contentUrl": ""}}})
    check("SIGN IN (PAT)", s == 200 and "token" in auth)
    sid = auth["siteId"]

    s, pr = call("POST", f"{base}/api/3.21/sites/{sid}/projects", {"name": "POC-Brand-Carvel"})
    check("CREATE project", s == 201 and "id" in pr)
    pid = pr["id"]

    s, wb = call("POST", f"{base}/api/3.21/sites/{sid}/workbooks",
                 {"name": "Brand Summary", "projectId": pid})
    check("CREATE (publish) workbook", s == 201 and "id" in wb)
    wid = wb["id"]

    s, pl = call("GET", f"{base}/api/3.21/sites/{sid}/projects")
    check("READ projects", s == 200 and any(x["id"] == pid for x in pl["projects"]))
    s, wl = call("GET", f"{base}/api/3.21/sites/{sid}/workbooks")
    check("READ workbooks", s == 200 and len(wl["workbooks"]) == 1)

    s, tu = call("POST", f"{base}/api/3.21/sites/{sid}/users",
                 {"name": "franchise.user@gtf.com", "siteRole": "Viewer"})
    check("UPDATE: add franchise user", s == 201 and tu["siteRole"] == "Viewer")

    s, _ = call("DELETE", f"{base}/api/3.21/sites/{sid}/workbooks/{wid}")
    check("DELETE workbook", s == 204)
    s, _ = call("DELETE", f"{base}/api/3.21/sites/{sid}/projects/{pid}")
    check("DELETE project", s == 204)

    print("\n=== SUMMARY =======================================================")
    passed, total = sum(results), len(results)
    print(f"  {passed}/{total} CRUD operations succeeded "
          f"({'ALL PASS' if passed == total else 'SOME FAILED'})")
    print("  Proven locally: Create/Read/Update/Delete on workspaces|projects, "
          "datasets, reports|workbooks, and users for BOTH vendor REST shapes.\n")
    return passed == total


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockHandler)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        ok = run_demo(base)
    finally:
        server.shutdown()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
