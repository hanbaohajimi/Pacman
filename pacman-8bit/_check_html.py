from pathlib import Path
import re

text = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
markers = re.findall(r"<!-- =============== SLIDE \d+ · .*? =============== -->", text)
positions = [text.index(m) for m in markers]
positions.append(len(text))

for i, m in enumerate(markers):
    chunk = text[positions[i] : positions[i + 1]]
    body = chunk[len(m) :]
    opens = body.count("<div")
    closes = body.count("</div>")
    status = "OK" if opens == closes else "MISMATCH"
    print(f"{m[30:55]:25} opens={opens} closes={closes} {status}")
