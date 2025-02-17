import json
from typing import List


def parse_lines(raw: str) -> List[str]:
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    out: List[str] = []
    for l in lines:
        try:
            obj = json.loads(l)
            msg = obj.get("message") or obj.get("msg") or obj.get("log") or l
            out.append(str(msg))
        except Exception:
            out.append(l)
    return out


def read_upload(upload) -> str:
    if upload is None:
        return ""
    b = upload.read()
    try:
        return b.decode("utf-8")
    except Exception:
        return b.decode("latin-1", errors="ignore")

