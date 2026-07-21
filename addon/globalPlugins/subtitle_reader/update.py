# coding=utf-8

import addonHandler

addonHandler.initTranslation()

import os
import re
from sys import version_info

if version_info.major == 2:
	from urllib import urlopen
	from codecs import open
else:
	from urllib.request import urlopen

import ssl
from threading import Thread


from .version import version
from .config import conf
from .gui import UpdateDialog, wx, gui as nvdaGui
from globalVars import appArgs

projectUrl = "https://raw.githubusercontent.com/hwangsihu/subtitle_reader/main"
sourceUrl = "https://raw.githubusercontent.com/hwangsihu/subtitle_reader/main/addon"
assetUrl = "https://github.com/hwangsihu/subtitle_reader/releases/latest/download"
tempDir = os.getenv("temp")


class Update:
	def __init__(self):
		self.new = {}
		self.checkThreadObj = None
		self.dialog = None
		self.downloadThreadObj = None
		self.checkAutomatic()

	def checkAutomatic(self):
		if not conf["checkUpdateAutomatic"]:
			return

		self.execute(automatic=True)
		self.automaticTimer = nvdaGui.NonReEntrantTimer(self.checkAutomatic)
		self.automaticTimer.StartOnce(1000 * 60 * 60 * 2)

	def manualCheck(self, event):
		conf["skipVersion"] = "0"
		self.execute()

	def openCurrentChangeLog(self, event):
		filePath = appArgs.configPath + r"\addons\subtitle_reader\doc\zh_TW\changelog.html"
		os.system("start " + filePath)

	def openLatestChangeLog(self, event):
		filePath = "https://github.com/hwangsihu/subtitle_reader/blob/main/addon/doc/zh_TW/changelog.md#%E6%9B%B4%E6%96%B0%E6%97%A5%E8%AA%8C"
		os.system("start " + filePath)

	def toggleCheckAutomatic(self, event):
		menu = event.GetEventObject()
		# Translators: This is Menu item that can toggle automatic check for update on Subtitle Reader is start
		id = menu.FindItem(_("Check for updates automatically (&A)"))
		item = menu.FindItemById(id)
		status = conf["checkUpdateAutomatic"] = not conf["checkUpdateAutomatic"]
		item.Check(status)

	def execute(self, automatic=False):
		if self.checkThreadObj and self.checkThreadObj.is_alive():
			return

		if self.dialog:
			return

		self.checkThreadObj = Thread(target=self.checkThread, kwargs={"automatic": automatic})
		self.checkThreadObj.start()

	def checkThread(self, automatic=False):
		try:
			info = self.getNewVersion()
		except Exception as e:
			if not automatic:
				wx.CallAfter(self.checkError, e)

			return

		if not info:
			if not automatic:
				wx.CallAfter(self.isLatestVersion)

			return

		if automatic and info["version"] == conf["skipVersion"]:
			return

		self.new = info
		wx.CallAfter(self.showDialog)

	def getNewVersion(self):
		info = {"version": 0, "changelog": "", "error": None}
		with urlopen(projectUrl + "/buildVars.py") as res:
			text = res.read().decode("utf-8")

		newVersion = re.findall(r'addon_version ?= ?"(.+)",\r?', text)[0]
		if newVersion == version:
			return

		info["version"] = newVersion

		with urlopen(sourceUrl + "/doc/zh_TW/changelog.md") as res:
			text = res.read().decode("utf-8")

		info["changelog"] = text
		return info

	def isLatestVersion(self):
		# Translators: This is a prompt to confirm that the reader is the latest version
		wx.MessageBox(
			_("You have updated to the latest version, enjoy using it!"),
			_("congratulations"),
			style=wx.ICON_EXCLAMATION,
		)

	def checkError(self, error):
		# Translators: This is the prompt when checking for updates fails
		wx.MessageBox(_("Unable to check for updates") + ": " + str(error), _("Error"), style=wx.ICON_ERROR)

	def showDialog(self):
		dlg = self.dialog = UpdateDialog(self.new["version"])
		dlg.isVisited = False
		dlg.changelogText.SetValue(self.new["changelog"])
		dlg.updateNow.Bind(wx.EVT_BUTTON, self.updateNow)
		dlg.skipVersion.Bind(wx.EVT_BUTTON, self.skipVersion)
		dlg.later.Bind(wx.EVT_BUTTON, self.later)
		dlg.Bind(wx.EVT_CLOSE, self.onClose)
		# nvdaGui.runScriptModalDialog(dlg)
		dlg.ShowWithoutActivating()

	def updateNow(self, event):
		if self.downloadThreadObj and self.downloadThreadObj.is_alive():
			return

		self.dialog.changelogText.SetFocus()
		self.downloadThreadObj = Thread(target=self.downloadThread)
		self.downloadThreadObj.start()

	def downloadThread(self):
		filename = "subtitle_reader.nvda-addon"
		try:
			file = self.downloadFile(
				assetUrl + "/" + filename,
				tempDir + "\\" + filename,
				reportHook=self.updateProgress,
			)
			self.dialog.Close()
			os.system("start " + file[0])
		except Exception as e:
			wx.CallAfter(self.downloadError, e)

	def downloadFile(self, url, filePath, reportHook=None):
		# 下載 release 再學校或辦公室出現憑證無效的問題，所以我們自備憑證。
		ctx = ssl.create_default_context(cafile=os.path.dirname(__file__) + r"\assets\cacert.pem")
		with urlopen(url, context=ctx) as response:
			total = int(response.headers.get("Content-Length", 0))
			current = 0
			with open(filePath, "wb") as f:
				while True:
					data = response.read(8192)
					if not data:
						break

					f.write(data)
					current += len(data)
					if reportHook:
						reportHook(current, total)

		if current < total:
			raise Exception("Download failed, Size mismatch. ")

		return filePath, response.headers

	def updateProgress(self, current, total):
		percent = int(100 * current / total)
		wx.CallAfter(self.dialog.progress.SetValue, percent)

	def downloadError(self, error):
		# Translators: This is the prompt when downloading updates fails
		wx.MessageBox(
			_("The update download has failed") + ": " + str(error),
			_("Error"),
			style=wx.ICON_ERROR,
			parent=self.dialog,
		)

	def skipVersion(self, event):
		conf["skipVersion"] = self.new["version"]
		self.dialog.Close()

	def later(self, event):
		self.dialog.Close()

	def onClose(self, event):
		self.dialog.Destroy()
		self.dialog = None
