#encoding=utf-8

from __future__ import absolute_import
from __future__ import unicode_literals

import addonHandler
addonHandler.initTranslation()

import wx
import gui
from gui.nvdaControls import EnhancedInputSlider

from .subtitleExtractors import SubtitleExtractor

tray = gui.mainFrame.sysTrayIcon
toolsMenu = tray.toolsMenu

class Menu(wx.Menu):
	def __init__(self, main):
		super(Menu, self).__init__()
		self.main = main
		# Translators: Subtitle Reader menu on the NVDA tools menu
		self.menuItem = toolsMenu.AppendSubMenu(self, _('Subtitle reader (&R)'))
		# Translators: Reader toggle switch on the Subtitle Reader menu
		self.switch = self.AppendCheckItem(wx.ID_ANY, _('Enable or disable subtitle reader (&S)'))
		self.switch.Check(True)
		
		# Translators: toggle reading when video window not in foreground on the Subtitle Reader menu
		self.backgroundReading = self.AppendCheckItem(wx.ID_ANY, _('Reading in the background (&B)'))
		self.backgroundReading.Check(True)
		
		self.youtube = wx.Menu()
		self.youtubeMenuItem = self.AppendSubMenu(self.youtube, _('Opciones for Youtube'))
		
		# Translators: toggle Youtube menu item whether to read the chat message when the new chat message already appeared
		self.readChat = self.youtube.AppendCheckItem(wx.ID_ANY, _('Read chat (&R)'))
		self.readChat.Check(True)
		
		# Translators: toggle Youtube menu item whether to read the chat message sender. 
		self.readChatSender = self.youtube.AppendCheckItem(wx.ID_ANY, _("Read the sender's name (&A)"))
		self.readChatSender.Check(True)
		
		# Translators: toggle Youtube menu item whether to read the manager's chat message only.
		self.onlyReadManagersChat = self.youtube.AppendCheckItem(wx.ID_ANY, _('Read only messages from the moderator (&M)'))
		self.onlyReadManagersChat.Check(False)
		
		# Translators: toggle Youtube menu item whether to read the chat gift sponser message. 
		self.readChatGiftSponser = self.youtube.AppendCheckItem(wx.ID_ANY, _('Read gift sent (&G)'))
		self.readChatGiftSponser.Check(True)
		
		# Translators: toggle Youtube menu item whether to omit graphic when reading the chats
		self.omitChatGraphic = self.youtube.AppendCheckItem(wx.ID_ANY, _('Skip the picture name when reading the chat (&G)'))
		self.omitChatGraphic.Check(True)
		
		# Translators: toggle menu item whether to prompt wher Youtube info card is already appear
		self.infoCardPrompt = self.youtube.AppendCheckItem(wx.ID_ANY, _('Information cards (&I)'))
		self.infoCardPrompt.Check(True)
		
		# Crunchyroll setup submenu
		self.crunchyrollSetup = wx.Menu()
		self.crunchyrollSetupMenuItem = self.AppendSubMenu(self.crunchyrollSetup, _('Crunchyroll - Setup (&K)'))
		# Tampermonkey submenu
		self.crunchyrollTM = wx.Menu()
		self.crunchyrollSetup.AppendSubMenu(self.crunchyrollTM, _('Install Tampermonkey (&T)'))
		self.crunchyrollTMChrome = self.crunchyrollTM.Append(wx.ID_ANY, 'Chrome (&C)')
		self.crunchyrollTMFirefox = self.crunchyrollTM.Append(wx.ID_ANY, 'Firefox (&F)')
		self.crunchyrollTMEdge = self.crunchyrollTM.Append(wx.ID_ANY, 'Edge (&E)')
		# Install userscript
		self.crunchyrollInstallScript = self.crunchyrollSetup.Append(wx.ID_ANY, _('Install script (&I)'))
		self.crunchyrollSetup.AppendSeparator()
		# Help
		self.crunchyrollHelp = self.crunchyrollSetup.Append(wx.ID_ANY, _('Help (&H)'))
		
		# Translators: This menu item performs a check for updates to the reader
		self.checkForUpdate = self.Append(wx.ID_ANY, _('Check for updates (&C)'))
		# Translators: This is menu item that open the current version's changelog
		self.openCurrentChangeLog = self.Append(wx.ID_ANY, _('Open current version change log (&O)'))
		# Translators: This is menu item that open the latest version's changelog
		self.openLatestChangeLog = self.Append(wx.ID_ANY, _('Open latest version change log (&L)'))
		# Translators: This menu item that can toggle automatic check for update when Subtitle Reader is start
		self.checkUpdateAutomatic = self.AppendCheckItem(wx.ID_ANY, _('Check for updates automatically (&A)'))
		self.checkUpdateAutomatic.Check(True)
		
		self.contactDeveloper = wx.Menu()
		self.contactDeveloperMenuItem = self.AppendSubMenu(self.contactDeveloper, _('contact the developer (&C)'))
		
		self.contactUseWhatsApp = self.contactDeveloper.Append(wx.ID_ANY, 'WhatsApp, id:+886925285060')
		self.contactUseFacebook = self.contactDeveloper.Append(wx.ID_ANY, _('Facebook profile'))
		self.contactUseQq = self.contactDeveloper.Append(wx.ID_ANY, _('QQ, id:2231691423'))
		self.contactUseLine = self.contactDeveloper.Append(wx.ID_ANY, 'Line, id:Maxe0310 ' + _('Click to copy'))
		self.contactUseDiscord = self.contactDeveloper.Append(wx.ID_ANY, 'Discord, ID:maxe0310 ' + _('Click to copy'))
		self.contactUseX = self.contactDeveloper.Append(wx.ID_ANY, _('X, ID:Maxe0310'))
		
		self.AppendSeparator()

		self.platforms = wx.Menu()
		self.platformsMenuItem = self.AppendSubMenu(self.platforms, _('Supported video platforms (&P)'))
		for platform in SubtitleExtractor.extractors:
			self.platforms.Append(wx.ID_ANY, platform.info['name'] + _(' State：') + platform.info['status'], platform.info['url'])
		
	

class UpdateDialog(wx.Dialog):
	def __init__(self, version):
		super(UpdateDialog, self).__init__(gui.mainFrame, wx.ID_ANY, title=_('Subtitle reader V') + str(version) + _(' Version information'))
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		# Translators: This label means the edit box content is changelog
		self.changelogLabel = wx.StaticText(self, label=_('Change log'))
		self.sizer.Add(self.changelogLabel)
		self.changelogText = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL, size=(1024, 768))
		self.sizer.Add(self.changelogText, wx.SizerFlags(1).Expand())
		
		self.subtitleLabel = Label(self, label=_('Subtitle'))
		self.sizer.Add(self.subtitleLabel, wx.SizerFlags(0).Center())
		
		self.volumeLabel = wx.StaticText(self, label='音樂音量')
		self.volumeSlider = EnhancedInputSlider(self, value=70)
		self.sizer.Add(self.volumeLabel)
		self.sizer.Add(self.volumeSlider)
		
		self.progress = wx.Gauge(self, style=wx.GA_VERTICAL + wx.ST_NO_AUTORESIZE)
		self.sizer.Add(self.progress)
		self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.buttonSizer, wx.SizerFlags(0).Center())
		# Translators: This button means now run the update process
		self.updateNow = wx.Button(self, label=_('Update now (&U)'))
		self.buttonSizer.Add(self.updateNow, wx.SizerFlags(1).Bottom())
		self.buttonSizer.AddStretchSpacer(1)
		# Translators: This button means that the automatic check for updates will skip this version
		self.skipVersion = wx.Button(self, label=_('Skip this version (&S)'))
		self.buttonSizer.Add(self.skipVersion, wx.SizerFlags(1).Bottom())
		self.buttonSizer.AddStretchSpacer(1)
		# Translators: This button means close window until next automatic or manual check for update
		self.later = wx.Button(self, label=_('Later (&L)'))
		self.buttonSizer.Add(self.later, wx.SizerFlags(1).Bottom())
		
		self.SetSizerAndFit(self.sizer)
		self.CenterOnScreen()
	

class Label(wx.StaticText):
	def AcceptsFocus(self):
		return True
	
	def AcceptsFocusFromKeyboard(self):
		return True
	
