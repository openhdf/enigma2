SUBDIRS = include lib main data po tools

ACLOCAL_AMFLAGS = -I m4

installdir = $(pkglibdir)/python
install_PYTHON = upgrade.py \
	Navigation.py NavigationInstance.py RecordTimer.py PowerTimer.py SleepTimer.py ServiceReference.py \
	keyids.py keymapparser.py mytest.py skin.py timer.py GlobalActions.py \
	e2reactor.py

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = enigma2.pc

metadir = $(datadir)/meta
meta_DATA = index-enigma2.xml
CLEANFILES = index-enigma2.xml

EXTRA_DIST = lamedb

index-enigma2.xml: $(top_srcdir)/tools/genmetaindex.py $(top_srcdir)/lib/python/Plugins/*/*/meta/plugin_*.xml
	$(AM_V_GEN)$(PYTHON) $^ > $@

dist_installdir = $(DESTDIR)/etc/enigma2
dist_install_DATA = \
	bouquets.tv \
	bouquets.radio \
	lamedb \
	userbouquet.bef001.tv \
	userbouquet.bef002.tv \
	userbouquet.bef003.tv \
	userbouquet.bef004.tv \
	userbouquet.bef005.tv \
	userbouquet.bef006.tv \
	userbouquet.bef007.tv \
	userbouquet.bef001.radio \
	userbouquet.bef002.radio \
	userbouquet.bef003.radio \
	userbouquet.bef004.radio \
	userbouquet.bef005.radio \
	userbouquet.bef006.radio \
	userbouquet.bef007.radio \
	userbouquet.dbe00.tv \
	userbouquet.favourites.tv \
	userbouquet.favourites.radio \
	userbouquet.hd.tv \
	userbouquet.kinder.tv \
	userbouquet.musik.tv \
	userbouquet.sky__tv_.tv

