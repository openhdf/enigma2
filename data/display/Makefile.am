installdir = $(pkgdatadir)/display/skin_default

if HAVE_TEXTLCD
DISPLAYTYPE = text
else
DISPLAYTYPE = display
endif

if HAVE_TEXTLCD
SUBDIRS = displaytext
endif

if HAVE_COLORLCD2
SUBDIRS = display96
endif

if HAVE_COLORLCD220
SUBDIRS = display220
endif

if HAVE_COLORLCD390
SUBDIRS = display390
endif

if HAVE_COLORLCD400
if GB7252
SUBDIRS = display400gb4k
else
SUBDIRS = display400
endif
endif

if HAVE_7SEGMENT
SUBDIRS = 7segment
endif

dist_install_DATA = skin_display.xml

# Use box-specific XML if it exists, otherwise get the default
# TEXTSKIN is either "default" or "7segment"
# TODO: Missing dependency on optional "skin_$(DISPLAYTYPE)_$(MACHINEBUILD).xml"
skin_display.xml:
	cp $(srcdir)/skin_$(DISPLAYTYPE)_$(MACHINEBUILD).xml $@ 2>/dev/null || cp $(srcdir)/skin_display.xml $@
