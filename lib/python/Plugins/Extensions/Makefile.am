installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = TuxboxPlugins CutListEditor PicturePlayer MediaScanner MediaPlayer SocketMMI DVDBurn VirtualZap GraphMultiEPG Volume_adjust AtileHD StreamlinkWrapper YTDLWrapper YTDLPWrapper

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if GB7252
SUBDIRS += QuadPip
endif

install_PYTHON =	\
	__init__.py
