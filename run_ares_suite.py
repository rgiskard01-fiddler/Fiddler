import argparse, json, uuid, time
from pathlib import Path

def call_router(prompt: str, conversation_id: str | None = None) -> dict:
    """
    IMPLEMENT ME.
    Return a dict with at least:
      - route (str): chosen route/model/tool tier
      - action (str): allow/refuse/tool/escalate/etc
      - notes (str): optional
    """
    return {"route":"UNKNOWN", "action":"UNIMPLEMENTED", "notes":"Implement call_router() in run_ares_suite.py"}

def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["single","multiturn"], required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_rows = []
    start = time.time()

    if args.mode == "single":
        suite_path = Path(__file__).with_name("ares_suite.jsonl")
        for test in load_jsonl(suite_path):
            run_id = str(uuid.uuid4())
            resp = call_router(test["prompt"])
            out_rows.append({
                "run_id": run_id,
                "test_id": test["id"],
                "class": test["class"],
                "expected_outcome": test["expected_outcome"],
                "prompt": test["prompt"],
                "router_response": resp,
            })
    else:
        suite_path = Path(__file__).with_name("ares_suite_multiturn.jsonl")
        for test in load_jsonl(suite_path):
            conversation_id = str(uuid.uuid4())
            turn_responses = []
            for i, turn in enumerate(test["turns"], start=1):
                resp = call_router(turn, conversation_id=conversation_id)
                turn_responses.append({
                    "turn": i,
                    "prompt": turn,
                    "router_response": resp,
                })
            out_rows.append({
                "conversation_id": conversation_id,
                "test_id": test["id"],
                "class": test["class"],
                "expected_outcome": test["expected_outcome"],
                "turns": turn_responses,
            })

    out_path = Path(args.out)
    write_jsonl(out_path, out_rows)
    dur = time.time() - start
    print(f"Wrote {len(out_rows)} result records to {out_path} in {dur:.1f}s")

if __name__ == "__main__":
    main()
