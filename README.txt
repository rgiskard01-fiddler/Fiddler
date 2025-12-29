ARES Router Attack Model v1.0 — Ready-to-Run Test Suite

Files:
- ARES_Mode_Spec_v1.0.txt
- Binder_Index_Insert_ARES.txt
- ares_suite.jsonl                 (single-turn tests)
- ares_suite_multiturn.jsonl       (multi-turn sequences)
- ares_suite.csv                   (single-turn tests in CSV)
- run_ares_suite.py                (runner harness; implement call_router())

Quickstart (Windows):
1) Install Python 3.11+
2) (Optional) pip install requests
3) Implement call_router() in run_ares_suite.py to call your router.
4) Run:
   python run_ares_suite.py --mode single --out ares_results.jsonl
   python run_ares_suite.py --mode multiturn --out ares_results_multiturn.jsonl

Then generate your KPI report from the result JSONL.
