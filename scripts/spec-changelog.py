#!/usr/bin/env python3

import re

SECTION_RE = r"%(changelog)"

found = False
changelog = ""

with open("crystalfontz.spec", "r") as f:
    it = iter(f)
    try:
        while True:
            line = next(it)
            m = re.findall(SECTION_RE, line)
            if not found and m and m[0] == "changelog":
                found = True
            elif found and m:
                # Found next section
                break
            elif found:
                changelog += line
            else:
                continue
    except StopIteration:
        pass

if not found:
    raise Exception("Could not find changelog in crystalfontz.spec")

print(changelog.strip())
