# -*- coding: utf-8 -*-
from __future__ import absolute_import

from twisted.internet import defer, reactor, ssl
from twisted.web import client

from os import unlink
import requests
from urllib.request import urlopen, Request
from enigma import eTimer

class HTTPProgressDownloader(client.HTTPDownloader):
	def __init__(self, url, outfile, headers=None):
		client.HTTPDownloader.__init__(self, url, outfile, headers=headers, agent="Enigma2 HbbTV/1.1.1 (+PVR+RTSP+DL;OpenHDF;;;)")
		self.status = self.progress_callback = self.error_callback = self.end_callback = None
		self.deferred = defer.Deferred()

	def noPage(self, reason):
		if self.status == b"304":
			print(reason.getErrorMessage())
			client.HTTPDownloader.page(self, "")
		else:
			client.HTTPDownloader.noPage(self, reason)
		if self.error_callback:
			self.error_callback(reason.getErrorMessage(), self.status)

	def gotHeaders(self, headers):
		if self.status == b"200":
			if b"content-length" in headers:
				self.totalbytes = int(headers[b"content-length"][0])
			else:
				self.totalbytes = 0
			self.currentbytes = 0.0
		return client.HTTPDownloader.gotHeaders(self, headers)

	def pagePart(self, packet):
		if self.status == b"200":
			self.currentbytes += len(packet)
		if self.totalbytes and self.progress_callback:
			self.progress_callback(self.currentbytes, self.totalbytes)
		return client.HTTPDownloader.pagePart(self, packet)

	def pageEnd(self):
		ret = client.HTTPDownloader.pageEnd(self)
		if self.end_callback:
			self.end_callback()
		return ret


class DownloadWithProgress:
	def __init__(self, url, outputFile):
		self.url = url
		self.outputFile = outputFile
		self.userAgent = "Enigma2 HbbTV/1.1.1 (+PVR+RTSP+DL;OpenHDF;;;)"
		# self.agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5"
		self.totalSize = 0
		self.progress = 0
		self.progressCallback = None
		self.endCallback = None
		self.errorCallback = None
		self.stopFlag = False
		self.timer = eTimer()
		self.timer.callback.append(self.reportProgress)

	def start(self):
		try:
			request = Request(self.url, None, {"User-agent": self.userAgent})
			feedFile = urlopen(request)
			metaData = feedFile.headers
			self.totalSize = int(metaData.get("Content-Length", 0))
			# Set the transfer block size to a minimum of 1K and a maximum of 1% of the file size (or 128KB if the size is unknown) else use 64K.
			self.blockSize = max(min(self.totalSize // 100, 1024), 131071) if self.totalSize else 65536
		except OSError as err:
			if self.errorCallback:
				self.errorCallback(err)
			return self
		reactor.callInThread(self.run)
		return self

	def run(self):
		# requests.Response object = requests.get(url, params=None, allow_redirects=True, auth=None, cert=None, cookies=None, headers=None, proxies=None, stream=False, timeout=None, verify=True)
		response = requests.get(self.url, headers={"User-agent": self.userAgent}, stream=True)  # Streaming, so we can iterate over the response.
		try:
			with open(self.outputFile, "wb") as fd:
				for buffer in response.iter_content(self.blockSize):
					if self.stopFlag:
						response.close()
						fd.close()
						unlink(self.outputFile)
						return True
					self.progress += len(buffer)
					if self.progressCallback:
						self.timer.start(0, True)
					fd.write(buffer)
			if self.endCallback:
				self.endCallback(self.outputFile)
		except OSError as err:
			if self.errorCallback:
				self.errorCallback(err)
		return False

	def stop(self):
		self.stopFlag = True

	def reportProgress(self):
		self.progressCallback(self.progress, self.totalSize)

	def addProgress(self, progressCallback):
		self.progressCallback = progressCallback

	def addEnd(self, endCallback):
		self.endCallback = endCallback

	def addError(self, errorCallback):
		self.errorCallback = errorCallback

	def setAgent(self, userAgent):
		self.userAgent = userAgent

	def addErrback(self, errorCallback):  # Temporary supprt for deprecated callbacks.
		print("[Downloader] Warning: DownloadWithProgress 'addErrback' is deprecated use 'addError' instead!")
		self.errorCallback = errorCallback
		return self

	def addCallback(self, endCallback):  # Temporary supprt for deprecated callbacks.
		print("[Downloader] Warning: DownloadWithProgress 'addCallback' is deprecated use 'addEnd' instead!")
		self.endCallback = endCallback
		return self


class downloadWithProgress(DownloadWithProgress):  # Class names should start with a Capital letter, this catches old code until that code can be updated.
	pass