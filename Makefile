# -*- coding: us-ascii-unix -*-

NAME       = harbour-pan-transit
VERSION    = 0.2
LANGS      = $(basename $(notdir $(wildcard po/*.po)))
POT_FILE   = po/pan-transit.pot

DESTDIR    =
PREFIX     = /usr
DATADIR    = $(DESTDIR)$(PREFIX)/share/$(NAME)
DESKTOPDIR = $(DESTDIR)$(PREFIX)/share/applications
ICONDIR    = $(DESTDIR)$(PREFIX)/share/icons/hicolor

LCONVERT = $(or $(wildcard /usr/lib/qt5/bin/lconvert),\
$(wildcard /usr/lib/*/qt5/bin/lconvert))

check:
	pyflakes pan providers

clean:
	rm -rf dist
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .cache */.cache */*/.cache
	rm -f po/*~
	rm -f rpm/*.rpm

dist:
	$(MAKE) clean
	mkdir -p dist/$(NAME)-$(VERSION)
	cp -r `cat MANIFEST` dist/$(NAME)-$(VERSION)
	tar -C dist -cJf dist/$(NAME)-$(VERSION).tar.xz $(NAME)-$(VERSION)

define install-translations =
# GNU gettext translations for Python use.
mkdir -p $(DATADIR)/locale/$(1)/LC_MESSAGES
msgfmt po/$(1).po -o $(DATADIR)/locale/$(1)/LC_MESSAGES/pan-transit.mo
# Qt linguist translations for QML use.
mkdir -p $(DATADIR)/translations
$(LCONVERT) -o $(DATADIR)/translations/$(NAME)-$(1).qm po/$(1).po
endef

install:
	@echo "Installing Python files..."
	mkdir -p $(DATADIR)/pan
	cp pan/*.py $(DATADIR)/pan
	@echo "Installing QML files..."
	mkdir -p $(DATADIR)/qml
	cp qml/pan-transit.qml $(DATADIR)/qml/$(NAME).qml
	cp qml/[ABCDEFGHIJKLMNOPQRSTUVXYZ]*.qml $(DATADIR)/qml
	mkdir -p $(DATADIR)/qml/icons
	cp qml/icons/*.png $(DATADIR)/qml/icons
	mkdir -p $(DATADIR)/qml/js
	cp qml/js/*.js $(DATADIR)/qml/js
	@echo "Installing providers..."
	mkdir -p $(DATADIR)/providers
	cp providers/*.json $(DATADIR)/providers
	cp providers/[!_]*.py $(DATADIR)/providers
	cp providers/README.md $(DATADIR)/providers
	mkdir -p $(DATADIR)/providers/digitransit
	cp providers/digitransit/*.graphql $(DATADIR)/providers/digitransit
	@echo "Installing translations..."
	$(foreach lang,$(LANGS),$(call install-translations,$(lang)))
	@echo "Installing desktop file..."
	mkdir -p $(DESKTOPDIR)
	cp data/$(NAME).desktop $(DESKTOPDIR)
	@echo "Installing icons..."
	mkdir -p $(ICONDIR)/86x86/apps
	mkdir -p $(ICONDIR)/108x108/apps
	mkdir -p $(ICONDIR)/128x128/apps
	mkdir -p $(ICONDIR)/256x256/apps
	cp data/pan-transit-86.png  $(ICONDIR)/86x86/apps/$(NAME).png
	cp data/pan-transit-108.png $(ICONDIR)/108x108/apps/$(NAME).png
	cp data/pan-transit-128.png $(ICONDIR)/128x128/apps/$(NAME).png
	cp data/pan-transit-256.png $(ICONDIR)/256x256/apps/$(NAME).png

pot:
	truncate -s0 $(POT_FILE)
	xgettext \
	 --output=$(POT_FILE) \
	 --language=Python \
	 --from-code=UTF-8 \
	 --join-existing \
	 --keyword=_ \
	 --add-comments=TRANSLATORS: \
	 --no-wrap \
	 */*.py

	xgettext \
	 --output=$(POT_FILE) \
	 --language=JavaScript \
	 --from-code=UTF-8 \
	 --join-existing \
	 --keyword=tr:1 \
	 --keyword=qsTranslate:2 \
	 --add-comments=TRANSLATORS: \
	 --no-wrap \
	 */*.qml qml/js/*.js

	cat */*.json \
	 | grep '^ *"_' \
	 | sed 's/: *\("[^"]*"\)/: _(\1)/' \
	 | sed 's/\("[^"]*"\)\(,\|]\)/_(\1)\2/g' \
	 | xgettext \
	    --output=$(POT_FILE) \
	    --language=JavaScript \
	    --from-code=UTF-8 \
	    --join-existing \
	    --keyword=_ \
	    --no-wrap \
	    -

rpm:
	$(MAKE) dist
	mkdir -p $$HOME/rpmbuild/SOURCES
	cp dist/$(NAME)-$(VERSION).tar.xz $$HOME/rpmbuild/SOURCES
	rm -rf $$HOME/rpmbuild/BUILD/$(NAME)-$(VERSION)
	rpmbuild -ba --nodeps rpm/$(NAME).spec
	cp $$HOME/rpmbuild/RPMS/noarch/$(NAME)-$(VERSION)-*.rpm rpm
	cp $$HOME/rpmbuild/SRPMS/$(NAME)-$(VERSION)-*.rpm rpm

test:
	py.test pan providers

.PHONY: check clean dist install pot rpm test
