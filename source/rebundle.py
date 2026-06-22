"""Re-bundle the standalone deck after editing `source/template.html`.

The deck is a single self-contained HTML file (`../index.html`) that wraps:
  - a base64+gzip manifest of fonts and the `deck-stage.js` runtime,
  - a small unpacker script,
  - a JSON-encoded HTML template (the actual slide markup).

This script reads the editable `source/template.html`, JSON-encodes it,
escapes inner </script> / </head> tags so the outer <script type="..."> is
not terminated early, and splices it back into `index.html`. The manifest
is untouched.

Usage:
    python rebundle.py              # rebundle in place
    python rebundle.py --verify     # roundtrip check (no write)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
BUNDLE = REPO / "index.html"
DECODED = HERE / "template.html"

TEMPLATE_OPEN = '<script type="__bundler/template">'
TEMPLATE_CLOSE = '</script>'


def splice_template(bundle_text: str, new_template_html: str) -> str:
    i = bundle_text.find(TEMPLATE_OPEN)
    if i < 0:
        raise SystemExit("Template open tag not found in bundle")
    payload_start = i + len(TEMPLATE_OPEN)
    j = bundle_text.find(TEMPLATE_CLOSE, payload_start)
    if j < 0:
        raise SystemExit("Template close tag not found in bundle")

    # JSON-encode the template. The template contains </script> and </head>;
    # those must be escaped as </script>/</head> in the JSON payload
    # so the outer <script type="__bundler/template"> is not terminated early
    # by the HTML parser before JSON.parse runs.
    encoded = json.dumps(new_template_html, ensure_ascii=False)
    encoded = encoded.replace("</", "<" + chr(92) + "u002F")

    return (
        bundle_text[:payload_start] + "\n" + encoded + "\n  " + bundle_text[j:]
    )


def main() -> int:
    bundle_text = BUNDLE.read_text(encoding="utf-8")
    decoded = DECODED.read_text(encoding="utf-8")

    new_bundle = splice_template(bundle_text, decoded)

    if "--verify" in sys.argv:
        if new_bundle == bundle_text:
            print("ROUNDTRIP OK: byte-identical")
            return 0
        for k, (a, b) in enumerate(zip(new_bundle, bundle_text)):
            if a != b:
                lo, hi = max(0, k - 40), k + 40
                print(f"ROUNDTRIP DIFFERS at byte {k}")
                print(f"  new:  ...{new_bundle[lo:hi]!r}")
                print(f"  orig: ...{bundle_text[lo:hi]!r}")
                break
        else:
            print(
                f"ROUNDTRIP DIFFERS in length only: "
                f"new={len(new_bundle)} orig={len(bundle_text)}"
            )
        return 1

    BUNDLE.write_text(new_bundle, encoding="utf-8")
    print(
        f"Rebundled: bundle={len(new_bundle):,} chars, "
        f"template={len(decoded):,} chars"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
