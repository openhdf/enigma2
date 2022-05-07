installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = TuxboxPlugins CutListEditor PicturePlayer MediaScanner MediaPlayer SocketMMI DVDBurn VirtualZap GraphMultiEPG Volume_adjust AtileHD MenuSort StreamlinkWrapper YTDLWrapper YTDLPWrapper

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

install_PYTHON =	\
	__init__.py
