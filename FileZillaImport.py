import sys
import os
import json
import sublime, sublime_plugin
from SitemanagerParser import SitemanagerParser

if sublime.platform() == 'linux':
	libpath = os.path.join(sublime.packages_path(), 'FilezillaImport', 'lib',
	        'linux-' + sublime.arch())
	sys.path.append(libpath)


class FilezillaImportCommand(sublime_plugin.WindowCommand):

	def run(self):
		items = [
			"Open FileZilla Sitemanager from default location",
			"Open other file" ]
		self.window.show_quick_panel(items, self.on_done)

	def on_done(self, index):
		if index == -1:
			return False
		elif index == 0:
			if sublime.platform() == 'windows':
				url = os.path.expandvars('%' + 'APPDATA%\FileZilla\sitemanager.xml')
			else:
				url = os.path.expanduser('~/.filezilla/sitemanager.xml')
			self.getServers(url)
		else:
		 	self.promptOtherFileLocation()

	def getServers(self, url):
		self.servers = SitemanagerParser(url).getServers()
		self.promptPickServer()
	
	def promptOtherFileLocation(self):
		self.window.show_input_panel('Input alternate file location', '', self.getServers, None, None)

	def promptPickServer(self):
		self.serverNames = self.servers.keys()
		self.window.show_quick_panel(self.serverNames, self.pickedServer)

	def pickedServer(self, index):
		if index == -1:
			return False
		serverName = self.serverNames[index]
		server = self.servers[serverName]
		self.createNewSftpConfig(server)
		
	def createNewSftpConfig(self, server):
		SFTP_default = """,
    
    "sync_down_on_open": true,
    
    //"file_permissions": "664",
    //"dir_permissions": "775",
    
    "connect_timeout": 30,
    //"ssh_key_file": "~/.ssh/id_rsa",
    //"sftp_flags": "-F /path/to/ssh_config",
    
    //"preserve_modification_times": false,
    //"remote_locale": "C",
}"""
		jsonString = json.dumps(server, indent = 4)
		jsonString = jsonString[:-2]
		jsonString += SFTP_default
		
		view = self.window.new_file()
		edit = view.begin_edit()
		view.insert(edit, 0, jsonString)
		view.end_edit(edit)
		view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')
