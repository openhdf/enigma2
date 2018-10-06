SUBDIRS = fonts extensions keymaps defaults

dist_pkgdata_DATA = \
	encoding.conf \
	keymap.xml \
	keytranslation.xml \
	keymap.ntr \
	keymap.u80 \
	keymap.xpe \
	keymap.lng \
	menu.xml \
	black.mvi \
	rcpositions.xml \
	restore.mvi \
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
SUBDIRS += displaytext
endif

if HAVE_COLORLCD2
SUBDIRS += display96
endif

if HAVE_COLORLCD1
SUBDIRS += display128
endif

if HAVE_COLORLCD3
SUBDIRS += display128dm
endif

if HAVE_BWLCD128
SUBDIRS += display128
endif

if HAVE_COLORLCD220
SUBDIRS += display220
endif

if HAVE_COLORLCD390
SUBDIRS += display390
endif

if HAVE_COLORLCD400
if GB7252
SUBDIRS += display400gb4k
else
SUBDIRS += display400
endif
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

if HAVE_GRAUTEC8000
SUBDIRS += grautec8000
endif

if HAVE_GRAUTEC70X0
SUBDIRS += grautec70x0
endif

if HAVE_7SEGMENT
SUBDIRS += 7segment
endif
