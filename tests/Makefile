.PHONY: locale
locale:
	@echo -n "Generate locale files"
	pybabel extract -F babel.conf -o ./locales/messages.po messages.py
	pybabel update -N -i ./locales/messages.po -d ./locales
	pybabel compile  -d ./locales

.PHONY: help
help:
	@echo -n "Common make targets"
	@echo ":"
	@cat Makefile | sed -n '/^\.PHONY: / h; /\(^\t@*echo\|^\t:\)/ {H; x; /PHONY/ s/.PHONY: \(.*\)\n.*"\(.*\)"/  make \1\t\2/p; d; x}'| sort -k2,2 |expand -t 20
