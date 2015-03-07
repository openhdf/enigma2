SUBDIRS = fonts extensions keymaps defaults

dist_pkgdata_DATA = \
	encoding.conf \
	keymap.xml \
	keymap.ntr \
	keymap.u80 \
	keymap.xpe \
	menu.xml \
	black.mvi \
	rcpositions.xml \
	setup.xml \
	skin_subtitles.xml \
	startwizard.xml \
	videowizard.xml \
	userinterfacepositionerwizard.xml \
	freesat.t1 \
	freesat.t2 \
	unicable.xml \
	hd-testcard.mvi \
	distro-logo.png \
	distro-lcd-logo.png

if HAVE_TEXTLCD
if SPARK
SUBDIRS += displaydualtext
else
SUBDIRS += displaytext
endif
endif

if HAVE_COLORLCD2
SUBDIRS += display96
endif

if HAVE_COLORLCD1
SUBDIRS += display128
endif

if HAVE_BWLCD128
SUBDIRS += display128
endif

if HAVE_COLORLCD220
SUBDIRS += display220
endif

if HAVE_COLORLCD400
SUBDIRS += display400
endif

if HAVE_COLORLCD720
SUBDIRS += display720
endif

if HAVE_BWLCD255
SUBDIRS += display255
endif

if HAVE_BWLCD140
SUBDIRS += display140
endif
