from __future__ import print_function
from . import _, PLUGIN_NAME, PLUGIN_VERSION
from Plugins.Plugin import PluginDescriptor
from .qpip import QuadPipScreen, setDecoderMode


def main(session, **kwargs):
	session.open(QuadPipScreen)


def autoStart(reason, **kwargs):
	if reason == 0:
		setDecoderMode("normal")
	elif reason == 1:
		setDecoderMode("normal")


def Plugins(**kwargs):
	list = []
	list.append(
		PluginDescriptor(name=_("Enable Quad PiP"),
		description=_("Quad Picture in Picture"),
		where=[PluginDescriptor.WHERE_EXTENSIONSMENU],
		fnc=main))

	list.append(
		PluginDescriptor(
		where=[PluginDescriptor.WHERE_AUTOSTART],
		fnc=autoStart))

	return list
