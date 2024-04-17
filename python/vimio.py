import vim
import os

class VimIO:
	breakpointGoodSignName="cmideGoodBreakpoint"
	breakpointBadSignName="cmideBadBreakpoint"
	breakpointSignGroup="cmideBreakpoints"
	breakpointSignPriority=10

	debugPosName="cmideDebugPos"
	debugPosGroup="cmideDebugPos"
	debugPosPriority=50

	filetypeByExt = {
		'.h':'cpp',
		'.hpp':'cpp',
		'.c':'cpp',
		'.cpp':'cpp'
	}

	def __init__(self, root):
		self.root = root
		self.bufToFile = {}
		self.bufToTab = {}
		self.fileToBuf = {}

		vim.command('sil call sign_define("%s", {"text": "O>", "texthl": "Debug"})' % VimIO.breakpointGoodSignName)
		vim.command('sil call sign_define("%s", {"text": "X>", "texthl": "Debug"})' % VimIO.breakpointBadSignName)
		vim.command('sil call sign_define("%s", {"text": "->", "texthl": "Debug"})' % VimIO.debugPosName)

	def clearBreakpointSigns(self):
		VimIO.__clearSignGroup(VimIO.breakpointSignGroup)

	def addBreakpointSign(self, isGood, filename, line):
		sign = VimIO.breakpointGoodSignName if isGood else VimIO.breakpointBadSignName
		self.__addSign(VimIO.breakpointSignGroup, sign, filename, line, VimIO.breakpointSignPriority)

	def clearDebugSign(self):
		VimIO.__clearSignGroup(VimIO.debugPosGroup)

	def addDebugSign(self, filename, line):
		self.__addSign(VimIO.debugPosGroup, VimIO.debugPosName, filename, line, VimIO.debugPosPriority)

	def __clearSignGroup(group):
		vim.command("sil call sign_unplace('%s')" % group)

	def __addSign(self, group, sign, filename, line, priority):
		cmd = "call sign_place(0, '%s', '%s', '%s', {'lnum' : %s, 'priotiry' : %s})" % (group, sign, self.getBufNum(filename), line, priority)
		vim.command(cmd)

	def __toRelative(self, path):
		return path if path.startswith('.') else os.path.relpath(path, self.root)

	def getBufNum(self, filename):
		return self.fileToBuf[filename] if filename in self.fileToBuf else 0


	def openFile(self, filename):
		if filename in self.fileToBuf:
			bufname = self.fileToBuf[filename]

			tabnum = self.bufToTab[bufname]
			if vim.bindeval('tabpagenr()') != tabnum:
				vim.command('tabn %d' % tabnum)

			winid = vim.bindeval('bufwinid(\'%s\')' % bufname)
			if vim.bindeval('win_getid()') != winid:
				vim.eval('win_gotoid(%s)' % winid)

			return bufname
		else:
			bufname = os.path.relpath(filename, self.root)
			self.fileToBuf[filename] = bufname
			self.bufToFile[bufname] = filename
			vim.command('tabe %s' % bufname)
			vim.command('set filetype=%s' % VimIO.filetypeByExt[os.path.splitext(filename)[1]])
			self.bufToTab[bufname] = vim.bindeval('tabpagenr()')

			return bufname

	def goToLine(self, filename, line):
		self.openFile(filename)
		vim.command(str(line))

	def openDebugWindows():
		vim.command('call cmide#ui#OpenDebugWindows()')

	def updateDebugWindows():
		vim.command('call cmide#ui#UpdateBuffers()')

	def getScope(name):
		return vim.vars if name == "" else vim.bindeval(name)

	def setVar(var, value):
		scopeIndex = var.find(':')
		VimIO.getScope(var[:scopeIndex + 1])[var[scopeIndex + 1:]] = value

	def updatedOpenedFiles(self):
		self.bufToFile.clear()
		self.bufToTab.clear()
		self.fileToBuf.clear()

		lastTabnum = vim.bindeval('tabpagenr("$")')
		for tabnum in range(1, lastTabnum + 1):
			bufids = vim.bindeval('tabpagebuflist("%d")' % tabnum)
			for bufid in bufids:
				bufname = vim.eval('bufname(%d)' % bufid)
				if bufname.startswith('.'):
					bufname = bufname[1:]
				filename = os.path.realpath(os.path.join(self.root, bufname))
				self.bufToFile[bufid] = filename
				self.bufToTab[bufid] = tabnum
				self.fileToBuf[filename] = bufid

	def getOpenedFiles(self):
		fileListLines = vim.eval('execute("ls a")')
		fileListNotparsed = fileListLines.split('\n')

		fileList = set()

		for notparsedFile in fileListNotparsed:
			if notparsedFile == "":
				continue

			firstQuote = notparsedFile.find('"')
			secondQuote = notparsedFile.find('"', firstQuote + 1)

			bufferName = notparsedFile[firstQuote + 1:secondQuote]

			# TODO might throw exception, cause not a path
			fileList.add(os.path.realpath(bufferName))

		return list(self.fileToBuf)

	def adaptStringList(vimList):
		result = []
		for vimString in vimList:
			result.append(vimString.decode(vim.eval("&encoding")))
		return result