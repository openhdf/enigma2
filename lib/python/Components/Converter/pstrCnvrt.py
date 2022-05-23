# -*- coding: utf-8 -*-
# by digiteng...12-2019

from Components.Converter.Converter import Converter
from Components.Element import cached
from json import load as jload
from re import search, sub
from os import path as os_path, mkdir

from six.moves import urllib
from six.moves.urllib.parse import quote


if not os_path.isdir('/tmp/poster'):
	mkdir('/tmp/poster')


class pstrCnvrt(Converter):

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type

	@cached
	def getText(self):
		event = self.source.event
		if event is None:
			return ''

		if not event is None:
			if self.type == 'POSTER':
				self.evnt = event.getEventName()
				try:
					p = '((.*?)) \([T](\d+)\)'
					e1 = search(p, self.evnt)
					if e1:
						jr = e1.group(1)
						self.evntNm = sub('\s+', '+', jr)
					else:
						self.evntNm = sub('\s+', '+', self.evnt)

					ses_ep = self.sessionEpisode(event)
					if ses_ep != '' and len(ses_ep) > 0:
						self.srch = 'tv'
						self.searchPoster()
					else:
						self.srch = 'multi'
						self.searchPoster()
					return self.evntNm
				except:
					pass
		else:
			return ''
	text = property(getText)

	def searchPoster(self):
		url_json = 'https://api.themoviedb.org/3/search/%s?api_key=3c3efcf47c3577558812bb9d64019d65&query=%s' % (self.srch, quote(self.evnt))
		jp = jload(urllib.request.urlopen(url_json))
		imgP = (jp['results'][0]['poster_path'])
		url_poster = 'https://image.tmdb.org/t/p/w185_and_h278_bestv2%s' % (imgP)
		dwn_poster = '/tmp/poster/poster.jpg'

		with open(dwn_poster, 'wb') as f:
			f.write(urllib.request.urlopen(url_poster).read())
			f.close()
			return self.evntNm

	def sessionEpisode(self, event):
		fd = event.getShortDescription() + '\n' + event.getExtendedDescription()
		pattern = ['(\d+). Staffel, Folge (\d+)', 'T(\d+) Ep.(\d+)', '"Episodio (\d+)" T(\d+)']
		for i in pattern:
			seg = search(i, fd)
			if seg:
				if search('Episodio', i):
					return 'S' + seg.group(2).zfill(2) + 'E' + seg.group(1).zfill(2)
				else:
					return 'S' + seg.group(1).zfill(2) + 'E' + seg.group(2).zfill(2)
		return ''
