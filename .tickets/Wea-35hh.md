---
id: Wea-35hh
status: closed
deps: []
links: []
created: 2026-04-06T20:29:20Z
type: task
priority: 2
assignee: Giles Weaver
external-ref: Weather-pt2
---
# Extract HTML into Jinja2 template

Move the ~330-line HTML/CSS/JS f-string in build_html() into a Jinja2 template file (templates/forecast.html) using [[ ]] delimiters. Separates presentation from data logic, unblocks Weather-fho and Weather-ibp.

