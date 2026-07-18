.PHONY: help svg png clean

help:
	@echo "svg    - сгенерировать SVG всех палитр и preview.html (python3 generate.py)"
	@echo "png    - сгенерировать SVG и конвертировать в PNG (1024x1024)"
	@echo "clean  - удалить сгенерированные svg, png и preview.html"

svg:
	python3 generate.py

png: svg
	for f in *.svg; do rsvg-convert -w 1024 -h 1024 $$f -o $${f%.svg}.png; done

clean:
	rm -f *.svg *.png preview.html
