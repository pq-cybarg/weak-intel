#!/usr/bin/env bash
# Reproduce graph, proofs, and site.
set -uo pipefail
cd "$(dirname "$0")"
if [ -x .venv/bin/python3 ]; then PATH="$(pwd)/.venv/bin:$PATH"; fi
JAVA="${JAVA:-$(command -v java || echo /Applications/Android\ Studio.app/Contents/jbr/Contents/Home/bin/java)}"
hr(){ printf '\n\033[1m%s\033[0m\n%s\n' "$1" "============================================================"; }

hr "[1] Canonical dual-use graph"
python3 models/graph/build_graph.py

hr "[2] Audit + cross-review"
python3 models/audit.py | tail -20
python3 models/cross_review.py | tail -20

hr "[3] Z3 shared substrate (S1-S3, B1-B2)"
python3 models/z3/shared_substrate.py

hr "[4] Z3 CRQC unwind (Q1-Q5)"
python3 models/z3/crqc_unwind.py

hr "[5] Site (bubblemap / dashboard / globe)"
python3 models/graph/build_site.py

hr "[6] Tests"
python3 -m unittest discover -s tests -v

hr "[7] TLA+ leak cascade (optional; jar auto-fetch)"
mkdir -p models/tla
if [ ! -f models/tla/tla2tools.jar ]; then
  curl -fsSL -o models/tla/tla2tools.jar \
    https://github.com/tlaplus/tlaplus/releases/latest/download/tla2tools.jar || true
fi
if [ -f models/tla/tla2tools.jar ]; then
  ( cd models/tla
    echo "--- Inv_NoCascade (expect VIOLATED) ---"
    "$JAVA" -cp tla2tools.jar tlc2.TLC -config cascade.cfg LeakCascade.tla 2>&1 \
      | grep -E 'Error: Invariant|states generated|No error' | head -20 )
else
  echo "tla2tools.jar missing — skip"
fi

hr "[8] Alloy dual-use (optional)"
mkdir -p models/alloy
if [ ! -f models/alloy/alloy.jar ]; then
  curl -fsSL -o models/alloy/alloy.jar \
    https://github.com/AlloyTools/org.alloytools.alloy/releases/download/v6.2.0/org.alloytools.alloy.dist.jar || true
fi
if [ -f models/alloy/alloy.jar ]; then
  ( cd models/alloy
    [ -f RunAlloy.class ] || "${JAVA%java}javac" -cp alloy.jar RunAlloy.java
    "$JAVA" -cp "alloy.jar:." RunAlloy DualUse.als 2>&1 | grep -E '===|command|instance' | head -20 )
else
  echo "alloy.jar missing — skip"
fi

echo
echo "Done. Open docs/index.html"
