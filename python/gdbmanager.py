import os
from enum import Enum
from pygdbmi.gdbcontroller import GdbController

class GdbManager:
	class RunningStatus(Enum):
		RUNNING = 1
		PAUSED = 2
		STOPPED = 3

	class Breakpoint:
		def __init__(self, filename, line):
			self.filename = os.path.realpath(filename)
			self.line = line

		def __eq__(self, other):
			return self.line == other.line and self.filename == other.filename

		def __hash__(self):
			return hash(self.filename) ^ hash(self.line)

	class CallInfo:
		def __init__(self, source, line):
			self.source = source
			self.line = line

	def __init__(self, root, onRun, onStop):
		self.gdbmi = GdbController()

		self.currentBinary = ''
		self.root = root

		self.breakpoints = set()
		self.callStack = []

		self.runningStatus = GdbManager.RunningStatus.STOPPED
		self.onRun = onRun
		self.onStop = onStop

	def checkDebuging(self):
		if self.runningStatus == GdbManager.RunningStatus.STOPPED:
			raise Exception("Executable is currently not under debug!")

	def __print(messages):
		for message in messages:
			messageType = message["type"]
			def _messageResultType(message):
				cases = {
					"error" : lambda m : print("Error: " + m["payload"]["msg"]),
					"done" : lambda m : print("Done"),
					"running" : lambda m : print("Running...")
				}
				messageType = message["message"]
				if not messageType in cases:
					print(message)
					return
				cases[messageType](message) 

			def _messageNotifyType(message):
				cases = {
					"thread-group-started" : lambda m : None,
					"thread-created" : lambda m : None,
					"library-loaded" : lambda m : None,
				}
				messageType = message["message"]
				if not messageType in cases:
					print("notify %s:%s" % (message["message"], message["payload"]))
					return
				cases[messageType](message) 

			cases = {
				"notify" : _messageNotifyType,
				"log" : lambda m : None,
				"console" : lambda m : print("console:%s" % m["payload"]),
				"output" : lambda m : print("output:%s" % m["payload"]),
				"result" : _messageResultType
			}
			if not messageType in cases:
				print(message)
				continue
			cases[messageType](message) 

	__ignoredMessageTypes = set(['log', 'console', 'result'])
	__ignoredMessages = set([
		'thread-group-started',
		'thread-created',	# TODO collect thread information
		'thread-exited',
		'library-loaded',
		'library-unloaded',
		'breakpoint-modified', # TODO use later
		])

	def __collectDebugInfo(self, messages):
		for message in messages:
			if message['type'] != 'notify':
				if message['type'] not in GdbManager.__ignoredMessageTypes:
					print(message)
				continue

			if message['message'] in GdbManager.__ignoredMessages:
				continue

			if message['message'] == 'running':
				self.__setRunningStatus(GdbManager.RunningStatus.RUNNING)
				continue
			if message['message'] == 'stopped':
				self.__setRunningStatus(GdbManager.RunningStatus.PAUSED)
				continue

			print(message)

	def __setRunningStatus(self, runningStatus):
		self.runningStatus = runningStatus
		if self.runningStatus != GdbManager.RunningStatus.STOPPED:
			self.onRun()
		else:
			self.onStop()

	def commandAndCollect(self, cmd):
		responce = self.__command(cmd)
		self.__collectDebugInfo(responce)

	def commandAndCollectExtra(self, cmd):
		print(cmd)
		responce = self.__command(cmd)
		GdbManager.__print(responce)
		self.__collectDebugInfo(responce)


	def commandWithIgnore(self, cmd):
		self.__command(cmd)

	def command(self, cmd):
		return self.__command(cmd)

	def __command(self, cmd):
		return self.gdbmi.write(cmd)

	def clearBinaries(self):
		self.clearBreakpoints()
		self.commandAndCollectExtra('file')

	def setExecutableBinary(self, binary):
		self.commandAndCollectExtra('file %s' % binary.replace("\\", "\\\\"))

	def addSharedLibrary(self, library):
		self.commandAndCollectExtra('symbol-file %s' % library.replace("\\", "\\\\"))

	def run(self):
		self.commandAndCollect('run')
		return self.updateCallStack()

	def cont(self):
		self.checkDebuging()
		self.commandAndCollect('continue')
		return self.updateCallStack()

	def stop(self):
		self.checkDebuging()
		self.commandAndCollectExtra('kill')

	def stepOver(self):
		self.checkDebuging()
		self.commandWithIgnore('next')
		return self.updateCallStack()

	def stepInto(self):
		self.checkDebuging()
		self.commandWithIgnore('step')
		return self.updateCallStack()

	def stepOut(self):
		self.checkDebuging()
		self.commandWithIgnore('finish')
		return self.updateCallStack()

	def stack(self):
		self.checkDebuging()
		self.commandAndCollectExtra('bt')

	def __breakFindSuccess(messages):
		for message in messages:
			if message['type'] == 'notify' and message['message'] == 'breakpoint-created':
				return True
		return False

	def isBreakpoint(self, filename, line):
		return GdbManager.Breakpoint(filename, line) in self.breakpoints

	def addBreakpoint(self, filename, line):
		if GdbManager.__breakFindSuccess(self.gdbmi.write('break %s:%s' % (filename, line))):
			self.breakpoints.add(GdbManager.Breakpoint(filename, line))
			return True
		else:
			return False

	def removeBreakpoint(self, filename, line):
		__breakpoint = GdbManager.Breakpoint(filename, line)
		if __breakpoint in self.breakpoints:
			self.commandWithIgnore('clear %s:%s' % (filename, line))
			self.breakpoints.discard(__breakpoint)

	def clearBreakpoints(self):
		self.breakpoints.clear()
		self.commandWithIgnore('delete')

	def updateCallStack(self):
		self.callStack.clear()
		response = self.gdbmi.write('bt')
		for message in response:
			if message['type'] != 'console':
				continue

			splitted = message['payload'].split(' ')
			if splitted[-2] == '??':
				self.callStack.append(GdbManager.CallInfo(splitted[0], -1))
				continue

			pathAndLineStr = message['payload'].split(' ')[-1]
			splitterPos = pathAndLineStr.rfind(":")
			path = pathAndLineStr[:splitterPos]
			line = pathAndLineStr[splitterPos + 1:]
			self.callStack.append(GdbManager.CallInfo(os.path.realpath(path), int(line)))

		return len(self.callStack) > 0

	def filterFilename(self, filename):
		return os.path.isfile(filename) and filename.startswith(self.root)

	def getCurrentFrame(self):
		self.checkDebuging()
		for callInfo in self.callStack:
			if not self.filterFilename(callInfo.source):
				continue

			return [callInfo.source, callInfo.line]

		return None