import vim
import os
import json

from cmakehelper import CMakeHelper
from gdbmanager import GdbManager
from vimio import VimIO
from ctags import CTags

from ctypes import windll
import traceback

def showMessage(message):
	message += '\nPython:\n' + ''.join(reversed(traceback.format_stack()[1:-1])) + 'Vim\n' + '\n'.join(reversed(vim.eval('expand("<stack>")').split('..')[1:]))
	#print(message)
	#windll.user32.MessageBoxW(0, message, "Info", 1)

class ACE:
	configHeader = 'main'
	configTarget = 'target'
	configBuildType = 'buildType'
	configSources = 'sources'

	class Source:
		def __init__(self, filename):
			self.filename = filename
			self.breakpoints = set()
			self.isOpened = False

		def toDict(self):
			return { 'breakpoints' : list(self.breakpoints), 'isOpened' : self.isOpened }

		def setOpened(self, isOpened):
			showMessage(self.filename + ": " + ("Opened" if isOpened else "Closed"))
			self.isOpened = isOpened

	def __init__(self, root, buildPath, buildTypes, cmakeGenerator, configFile):
		self.root = os.path.realpath(root)
		self.configFile = configFile

		self.vimio = VimIO(self.root)
		self.gdbManager = GdbManager(self.root, 
			lambda: self.__showDebugWindows(),
			lambda: self.__hideDebugWindows()
			)
		self.ctags = CTags(self.root)
		self.cmakeHelper = CMakeHelper(buildPath, buildTypes, cmakeGenerator)

		self.sources = {}

	def checkConfigured(self):
		self.cmakeHelper.checkConfigured()

	def checkDebuging(self):
		self.gdbManager.checkDebuging()

	def configure(self, silent):
		self.cmakeHelper.configure(silent)

	def saveToJson(self):
		os.makedirs(os.path.dirname(self.configFile), exist_ok=True)
		jsonStr = self.__formatToJson()
		with open(self.configFile, 'w') as jsonFile:
			jsonFile.write(jsonStr)

		showMessage("config saved")

	def __formatToJson(self):
		#self.checkConfigured()
		config = {
		    ACE.configTarget : self.cmakeHelper.activeTarget,
		    ACE.configBuildType : self.cmakeHelper.activeBuildType,
		    ACE.configSources : {k: v.toDict() for k, v in self.sources.items()}
		}
		return json.dumps(config)

	def loadFromJson(self):
		jsonStr = None
		with open(self.configFile, 'r') as jsonFile:
			jsonStr = jsonFile.read()
		self.__parseFromJson(jsonStr)

		showMessage("config loaded")

	def __parseFromJson(self, jsonStr):
		self.checkConfigured()
		config = json.loads(jsonStr)

		if ACE.configTarget in config:
			self.setTarget(config[ACE.configTarget])
		if ACE.configBuildType in config:
			self.cmakeHelper.activeBuildType = config[ACE.configBuildType]
		if ACE.configSources in config:
			self.sources.clear()
			fileOpened = False

			for sourcePath, sourceDict in config[ACE.configSources].items():
				source = self.__getSource(sourcePath)
				isOpened = sourceDict['isOpened']
				source.setOpened(isOpened)
				if isOpened:
					self.vimio.openFile(sourcePath)
					fileOpened = True
				source.breakpoints = set(sourceDict['breakpoints'])

			if fileOpened:
				vim.command('1tabc')
			self.onOpenedFileListChanged()

	def playButton(self):
		cases = {
			GdbManager.RunningStatus.RUNNING : lambda : self.pause(),
			GdbManager.RunningStatus.PAUSED : lambda : self.cont(),
			GdbManager.RunningStatus.STOPPED : lambda : self.run()
		}
		cases[self.gdbManager.runningStatus]()

	def run(self):
		self.cmakeHelper.build()
		self.gdbManager.run()
		self.updateDebugStack()

	def cont(self):
		self.gdbManager.cont()
		self.updateDebugStack()

	def pause(self):
		pass # TODO

	def stop(self):
		self.gdbManager.stop()
		self.updateDebugStack()

	def stepOver(self):
		self.gdbManager.stepOver()
		self.updateDebugStack()

	def stepInto(self):
		self.gdbManager.stepInto()
		self.updateDebugStack()

	def stepOut(self):
		self.gdbManager.stepOut()
		self.updateDebugStack()

	def flipBreakpoint(self, filename, line):
		filename = os.path.realpath(filename)
		if line not in self.__getSource(filename).breakpoints:
			self.__addBreakpoint(filename, line)
			self.updateBreakpoints()
			self.updateDebugStack()
		else:
			self.__removeBreakpoint(filename, line)

	def __addBreakpoint(self, filename, line):
		print("GDBAddBreakpoint")
		self.__getSource(filename).breakpoints.add(line)

	def __removeBreakpoint(self, filename, line):
		self.__getSource(filename).breakpoints.discard(line)
		self.gdbManager.removeBreakpoint(filename, line)

	def clearBreakpoints(self):
		self.gdbManager.clearBreakpoints()

	def __sourcesStateToStr(self):
		lines = []
		for filename, source in self.sources.items():
			lines.append(filename + ": " + ("Opened" if source.isOpened else "Closed"))

		return "\n".join(lines)

	def onOpenedFileListChanged(self):
		self.vimio.updatedOpenedFiles()
		openedFiles = self.vimio.getOpenedFiles()

		for openedFile in openedFiles:
			if not self.gdbManager.filterFilename(openedFile):
				continue
			self.__getSource(openedFile)

		for filename, source in self.sources.items():
			if source.isOpened and filename not in openedFiles:
				self.__onFileClosed(filename)
			elif not source.isOpened and filename in openedFiles:
				self.__onFileOpened(filename)

		# TODO instead just add breakpoints for freshly opened files
		self.updateBreakpoints()

		showMessage("FileListChanged!\n'%s'" % self.__sourcesStateToStr())

	def __onFileOpened(self, filename):
		self.__getSource(filename).setOpened(True)
		self.updateBreakpoints()

	def __onFileClosed(self, filename):
		self.__getSource(filename).setOpened(False)

	def updateBreakpoints(self):
		self.vimio.clearBreakpointSigns()
		for filename, source in self.sources.items():
			for line in source.breakpoints:
				if not self.gdbManager.isBreakpoint(filename, line):
					self.gdbManager.addBreakpoint(filename, line)

				if source.isOpened:
					self.vimio.addBreakpointSign(self.gdbManager.isBreakpoint(filename, line), filename, line)

	def __getSource(self, filename):
		if not filename in self.sources:
			newSource = ACE.Source(filename)
			self.sources[filename] = newSource
			return newSource
		else:
			return self.sources[filename]

	def __showDebugWindows(self):
		VimIO.openDebugWindows()

	def __hideDebugWindows(self):
		pass

	def updateDebugStack(self):
		self.vimio.clearDebugSign()

		if self.gdbManager.callStack == []:
			return

		currentFrame = self.gdbManager.getCurrentFrame()
		if currentFrame is None:
			return

		if not self.__getSource(currentFrame[0]).isOpened:
			self.vimio.openFile(currentFrame[0])

		self.vimio.goToLine(currentFrame[0], currentFrame[1])
		self.vimio.addDebugSign(currentFrame[0], currentFrame[1])

		VimIO.updateDebugWindows()

	def getTarget(self):
		return self.cmakeHelper.activeTarget

	def getTargetsList(self):
		return list(self.cmakeHelper.targets.keys())

	def setTarget(self, target):
		if target == self.cmakeHelper.activeTarget:
			return

		self.cmakeHelper.setTarget(target)

		self.__setBinaries()

		self.updateBreakpoints()

	def __setBinaries(self):
		binary = self.cmakeHelper.getActiveTargetBinary()
		if binary != '':
			self.gdbManager.clearBinaries()

			if os.path.isfile(binary) and os.access(binary, os.X_OK):
				self.gdbManager.setExecutableBinary(binary)

	def build(self):
		self.cmakeHelper.build()
		# TODO do not update it every time
		self.__setBinaries()

		self.updateBreakpoints()

	def getBuildType(self):
		return self.cmakeHelper.activeBuildType

	def getBuildTypesList(self):
		return self.cmakeHelper.buildTypes

	def setBuildType(self, buildType):
		if buildType == self.cmakeHelper.activeBuildType:
			return

		self.cmakeHelper.activeBuildType = buildType

		self.__setBinaries()

	def getCallStack(self):
		callStack = []
		for frame in self.gdbManager.callStack:
			callStack.append('%s:%s' % (os.path.relpath(frame.source, self.root), frame.line))
		return callStack

	def getIdProposeList(self, filename, pos, sourceLineBefore):
		return self.ctags.getIdProposeList(filename, pos, sourceLineBefore)

	def getIdUsageAtPosList(self, filename, pos, sourceLine, offset):
		return self.ctags.getIdUsageAtPosList(filename, pos, sourceLine, offset)

	def updateLine(self, filename, fromPos, toPos, newLine):
		return self.ctags.updateLine(filename, fromPos, toPos, newLine)
