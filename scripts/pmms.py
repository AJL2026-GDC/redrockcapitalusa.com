#!/usr/bin/env python3
"""Write rates.json from Freddie Mac's public PMMS history CSV.

Used by .github/workflows/pmms.yml (weekly) and by the local build.
Usage: pmms.py <csv-path-or-url> <out-json>
"""
import csv, io, json, sys, urllib.request
from datetime import datetime

SRC = "https://www.freddiemac.com/pmms/docs/PMMS_history.csv"


def load(src):
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"User-Agent": "redrockcapitalusa.com rates feed"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode("utf-8", "replace")
    return open(src, encoding="utf-8").read()


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else SRC
    out = sys.argv[2] if len(sys.argv) > 2 else "rates.json"
    rows = [r for r in csv.DictReader(io.StringIO(load(src))) if (r.get("pmms30") or "").strip()]
    if len(rows) < 2:
        sys.exit("PMMS CSV had no usable rows; leaving rates.json unchanged")
    cur, prev = rows[-1], rows[-2]

    def num(v):
        v = (v or "").strip()
        return float(v) if v else None

    week = datetime.strptime(cur["date"], "%m/%d/%Y").strftime("%Y-%m-%d")
    data = {
        "source": "Freddie Mac Primary Mortgage Market Survey (PMMS)",
        "source_url": "https://www.freddiemac.com/pmms",
        "week": week,
        "rates": [
            {"term": "30-year fixed", "rate": num(cur["pmms30"]), "prior": num(prev["pmms30"])},
            {"term": "15-year fixed", "rate": num(cur["pmms15"]), "prior": num(prev["pmms15"])},
        ],
    }
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(json.dumps(data))


if __name__ == "__main__":
    main()
