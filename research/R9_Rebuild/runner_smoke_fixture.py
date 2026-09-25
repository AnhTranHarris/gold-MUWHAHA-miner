#!/usr/bin/env python3
import json, os
from pathlib import Path
out=Path(os.environ["R9_TEST_OUT"]); out.mkdir(parents=True,exist_ok=True)
(out/"fixture.json").write_text(json.dumps({"ok":True}),encoding="utf-8")
print("fixture complete")
