.PHONY: test generic-install deb-package deb-install clean

PYEXEC := python3.7
NAME := gunka
UNDERSCORE = $(subst -,_,$(NAME))
DEBNAME = python3-$(NAME)

test:
	$(PYEXEC) -m pytest

generic-install:
	$(PYEXEC) setup.py install

deb-package:
	$(PYEXEC) setup.py --command-packages=stdeb.command bdist_deb
	mv deb_dist/$(DEBNAME)_*.deb .
	rm $(UNDERSCORE)-*.tar.gz
	rm -rf deb_dist dist $(UNDERSCORE).egg-info

deb-install: deb-package
	sudo dpkg -i $(DEBNAME)_*.deb

clean:
	rm $(DEBNAME)_*.deb || true
	rm $(UNDERSCORE)-*.tar.gz || true
	rm -rf deb_dist dist $(UNDERSCORE).egg-info || true
