#!/usr/bin/env python3
"""
update_prompt.py

Create or update the master prompt file (master_prompt.txt) used by the generator.
Run whenever you want to tweak generation rules, examples, or per-country guidance.
"""

from pathlib import Path
import argparse
import textwrap
import sys

MASTER_PROMPT_FILE = Path("master_prompt.txt")

MASTER_PROMPT_TEMPLATE = textwrap.dedent("""\
You are an address candidate generator that outputs realistic postal addresses intended for validation by an external validator.

Follow these rules STRICTLY:

1) Output format (exact): "{{house_number}} {{street_name}}, {{city}}, {{postcode}}, {{country}}"

   Example: "24 Market Street, Manchester, M1 1WR, United Kingdom"

2) ASCII only. No accented letters.

3) At least 3 commas per line (house/street, city, postcode, country).

4) Use **real** street names and real postal codes for the target country. Do NOT invent postal code formats.

   Prefer residential small streets, mews, courts, lanes, and "mews" — places likely to have small buildings.

5) Avoid large POIs, businesses, malls, industrial zones, or airports. Prefer residential parcels and small building footprints.

6) The generator should prioritize streets/areas known to have building polygons in OpenStreetMap.

7) Provide *only* addresses, one per line. No numbering, no commentary.

EXAMPLES (style references) — DO NOT REPEAT exactly:

- 24 Market Street, Manchester, M1 1WR, United Kingdom
- 32 High Street, Oxford, OX1 4AW, United Kingdom
- 15 King Edward Street, Oxford, OX1 4HL, United Kingdom

When asked to generate for a specific country, do not repeat the examples above; instead follow the format and use real local streets and postcodes.

Output exactly N addresses when the user asks, and be concise.

# End of master prompt
""")

def write_master_prompt(path: Path = MASTER_PROMPT_FILE, extra: str = ""):
    text = MASTER_PROMPT_TEMPLATE
    if extra:
        text += "\n\n# Extra guidance:\n" + extra.strip() + "\n"
    path.write_text(text, encoding="utf-8")
    print(f"Wrote master prompt to {path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra", help="extra guidance to append inside prompt (optional)", default="")
    parser.add_argument("--out", help="output file", default=str(MASTER_PROMPT_FILE))
    args = parser.parse_args()
    write_master_prompt(Path(args.out), args.extra)

if __name__ == "__main__":
    main()


