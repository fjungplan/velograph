from __future__ import annotations

import hashlib
import json
from typing import Any


def compute_etag(payload: Any) -> str:
    """Compute a stable ETag for a JSON-serializable payload.

    Uses SHA-256 of a canonical JSON dump (sorted keys, no whitespace).
    """
    try:
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    except TypeError:
        # Fallback: coerce to string if not JSON-serializable
        data = str(payload)
    digest = hashlib.sha256(data.encode("utf-8")).hexdigest()
    return f"W/\"{digest}\""
