"""File-based persistent state for the biosphere (git-friendly).

The planet's memory lives in-repo under ``bios/state/``:
  - ``capsules/*.json``  every capsule emitted (the biosphere's memory)
  - ``ledger.json``      tick count + capsule index

It accumulates across ticks: the biosphere never reboots blank.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List

from .contract import Capsule


class StateStore:
    def __init__(self, root: str):
        self.root = root
        self.caps_dir = os.path.join(root, "capsules")
        self.ledger = os.path.join(root, "ledger.json")
        os.makedirs(self.caps_dir, exist_ok=True)
        if not os.path.isfile(self.ledger):
            self._write({"ticks": 0, "capsules": []})

    def _read(self) -> Dict:
        with open(self.ledger, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _write(self, d: Dict) -> None:
        with open(self.ledger, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2)

    def append(self, cap: Capsule) -> None:
        d = self._read()
        fn = f"{cap.trace_id or 'x'}-{cap.tick:04d}-{cap.kind.value}.json"
        with open(os.path.join(self.caps_dir, fn), "w", encoding="utf-8") as fh:
            json.dump(cap.to_dict(), fh, indent=2)
        d["ticks"] = max(d["ticks"], cap.tick)
        d["capsules"].append(fn)
        self._write(d)

    def summary(self) -> str:
        d = self._read()
        return f"ticks={d['ticks']} capsules={len(d['capsules'])}"

    def capsules(self) -> List[str]:
        return self._read()["capsules"]
