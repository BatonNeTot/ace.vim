import subprocess
import sys
import os
import shutil
from enum import Enum

class CMakeHelper:
	class Status(Enum):
		NOT_READY = 1
		CONFIGURED = 2
		BUILDED = 3

	def __init__(self, buildPath, buildTypes, generator):
		self.buildPath = buildPath

		self.buildTypes = buildTypes
		self.activeBuildType = buildTypes[0]

		self.generator = generator
		
		self.targets = {}
		self.activeTarget = ''

		self.status = CMakeHelper.Status.NOT_READY

	def checkConfigured(self):
		if self.status == CMakeHelper.Status.NOT_READY:
			raise Exception("CMake is not configured!")


	def __getFullBuildPath(self):
		return os.path.join(self.buildPath, self.activeBuildType)

	def __systemCall(args, silent=False):
		result = subprocess.run(args, capture_output=True, text=True)
		if not silent:
			print(result.stdout)
		if result.returncode != 0:
			print(result.stdout)
			print(result.stderr, file=sys.stderr)
			return False
		return True

	def configure(self, silent):
		if not CMakeHelper.__systemCall(['cmake', '-S', '.', self.__getFullBuildPath(), '-G', self.generator, '-DCMAKE_BUILD_TYPE=' + self.activeBuildType
			#, '-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON'
			], silent):
			self.status = CMakeHelper.Status.NOT_READY
			return
		self.status = CMakeHelper.Status.CONFIGURED
		self.collectTargets()

	def build(self):
		self.checkConfigured()
		if not CMakeHelper.__systemCall(['cmake', '--build', self.__getFullBuildPath()]):
			self.status = CMakeHelper.Status.CONFIGURED
			return
		self.status = CMakeHelper.Status.BUILDED

	def clear(self):
		self.checkConfigured()
		CMakeHelper.__systemCall(['cmake', '--build', self.__getFullBuildPath(), '--target', 'clean'])
		shutil.rmtree(self.__getFullBuildPath())

	def collectTargets(self):
		self.checkConfigured()
		self.targets.clear()
		for root, dirs, _ in os.walk(os.path.join(self.__getFullBuildPath(), "CMakeFiles")):
			for name in dirs:
				if not name.endswith(".dir"):
					continue

				target = name[:-4]
				linkData = open(os.path.join(root, name, "link.txt"), "r").read()
				linkDataLines = linkData.split("\n")
				while linkDataLines[-1] == '':
					linkDataLines.pop()
				linkCmd = linkDataLines[-1]
				linkCmdArgs = linkCmd.split(" ")
				if "ranlib" in linkCmdArgs[0]:
					self.targets[target] = linkCmdArgs[1]
				elif "c++" in linkCmdArgs[0]:
					self.targets[target] = linkCmdArgs[linkCmdArgs.index("-o") + 1]
			break

		return self.targets

	def setTarget(self, target):
		self.checkConfigured()
		if target in self.targets:
			self.activeTarget = target

	def getActiveTargetBinary(self):
		self.checkConfigured()
		return self.targets[self.activeTarget] if self.activeTarget in self.targets else ''