"""Write _site/assets/i18n-en.js from i18n/en.json: the English dictionary a host site (MolAstria) uses to translate
the atlas with its own i18n.js. Keys are Chinese text as shown on the page; {0} {1} … are slots for numbers or names."""
import json
d = json.load(open("i18n/en.json", encoding="utf-8"))
js = "window.CHEMHUB_I18N_EN=" + json.dumps(d, ensure_ascii=False).replace("</", "<\\/") + ";\n"
open("_site/assets/i18n-en.js", "w", encoding="utf-8").write(js)
