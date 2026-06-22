# ISO ERC 2.0 Integration — slide deck

A self-contained, browser-openable deck describing the **ISO ERC integration** proof-of-concept: ingest → customer integration → deviations → algorithm view → content → bureau-grounded issuance → circulars.

## What's here

| File | Purpose |
|---|---|
| [`index.html`](./index.html) | The deck. Open in any modern browser — no server required. Self-contained: fonts and the slide runtime are inlined. |
| [`source/template.html`](./source/template.html) | The editable HTML template. This is where slide markup actually lives. |
| [`source/rebundle.py`](./source/rebundle.py) | Re-packs `template.html` into `index.html` after edits. Python 3.10+. |

## Editing the deck

1. Open `source/template.html` in your editor.
2. Make changes (slide content is grouped by `<section data-label="…">`).
3. Run:
   ```
   python source/rebundle.py
   ```
4. Open `index.html` in a browser to verify.

Optional sanity check:
```
python source/rebundle.py --verify
```
This roundtrip-tests the encode/decode without writing — useful when you suspect a bundle-level issue.

## How the bundle works

`index.html` is a Claude artifact bundle: a small unpacker script plus two embedded JSON payloads — a base64+gzip manifest of fonts and the `deck-stage.js` runtime, and the HTML template (JSON-encoded). On load, the unpacker decodes the manifest into blob URLs, substitutes them into the template, and renders the result.

Re-bundling only rewrites the template payload — the manifest stays untouched.
