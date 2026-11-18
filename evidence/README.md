# fgilywv4 — answer-key evidence (taiga-back @ 8ab6a4e3)

Validation evidence for the Taiga project-side review task. All file:line references and all
reproductions are at the pinned commit `8ab6a4e3b5f6fbbfcbf108a6449011f07b7308aa` (current upstream main).

## What is here

- **EVIDENCE.md** — for the 15 bugs the model missed and the 1 real bug it withdrew: setup, expected
  result, actual result at the pin, with a file:line and the proof script for each. Also lists the tag/
  attachment bugs separately.
- **SCORE.md** — the full accounting: 29 found / 15 missed, mapped to the model's final 40-row list,
  every item with a file:line and its proof script.
- **scripts/** — the proof scripts referenced by both documents. Each script was run over the HTTP API
  on a fresh instance (gunicorn, 4 workers + PostgreSQL 16), with low-privilege roles and two projects
  owned by different users where cross-project behaviour is involved; concurrency scripts fire real
  simultaneous requests.

## Script naming

A script that EVIDENCE.md or SCORE.md cites as e.g. `L1/scratch/r2/r2a03_status_delete_moveto_derived.py`
is stored here as `scripts/L1_r2_r2a03_status_delete_moveto_derived.py` (the original path with `/scratch/`
and the remaining `/` collapsed to `_`). The `L3_verify1_c03_05.py` / `c15_17.py` scripts each cover the
grouped cases cited as c03–c05 / c15, c17. `L3_verify1_common.py`, `inproc.py` and `listen.py` are shared
helpers for the L3 verification scripts.

## How to run

These scripts assume a running Taiga API at the pinned commit with PostgreSQL, reachable on a local port,
and an admin account. They were authored against the throwaway instances used to build the key; adjust the
base URL / credentials at the top of each script to your own instance. They are included as evidence of the
setup and the assertions behind each finding, not as a turnkey suite.
