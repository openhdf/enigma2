installdir = $(datadir)/fonts

dist_install_DATA = \
	*.ttf \
	*.otf

install-data-hook:
	cd $(DESTDIR)$(datadir)/fonts && \
	$(LN_S) wqy-microhei.ttc fallback.font
