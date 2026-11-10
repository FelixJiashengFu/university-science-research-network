"""Write _site/assets/i18n-en.js from i18n/en.json: the English dictionary a host site (MolAstria) uses to translate
the atlas with its own i18n.js. Keys are Chinese text as shown on the page; {0} {1} … are slots for numbers or names.
Stops when a school's Chinese name in assets/nav.js has no English entry: MolAstria's atlas-sync checks that the English
home page has no Chinese left, so a missing name would block every sync until it is added."""
import json, re, sys
d = json.load(open("i18n/en.json", encoding="utf-8"))
nav = open("assets/nav.js", encoding="utf-8").read()
missing = [zh for zh in re.findall(r'\["[\w-]+", "([^"]+)", "[^"]+", "(?:US|CA|CN)"', nav) if zh not in d]
if missing:
    sys.exit("i18n/en.json has no English for these school names in assets/nav.js: " + "、".join(missing))
js = "window.CHEMHUB_I18N_EN=" + json.dumps(d, ensure_ascii=False).replace("</", "<\\/") + ";\n"
open("_site/assets/i18n-en.js", "w", encoding="utf-8").write(js)
