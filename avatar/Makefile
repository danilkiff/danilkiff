# wildcard непригоден: в свежем чекауте svg ещё не сгенерированы
PALETTES := $(shell python3 -c 'import generate; print(" ".join(sorted(generate.PALETTES)))')
SVG := $(addsuffix .svg,$(PALETTES))
PNG := $(SVG:.svg=.png)

.PHONY: help svg png clean

help:
	@echo "svg    - сгенерировать SVG всех палитр (python3 generate.py)"
	@echo "png    - конвертировать *.svg в *.png (1024x1024, инкрементально)"
	@echo "clean  - удалить сгенерированные svg и png"

svg: $(SVG)

$(SVG): generate.py
	python3 generate.py

png: $(PNG)

%.png: %.svg
	rsvg-convert -w 1024 -h 1024 $< -o $@

clean:
	rm -f *.svg *.png
