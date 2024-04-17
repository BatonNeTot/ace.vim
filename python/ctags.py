import os
import json
from enum import Enum
from datetime import datetime
from bisect import bisect_left
import lalr
from clexer import *

class Parser:
	__impl = lalr.Model([
				lalr.Prod('States', 		[lalr.Nonterm('State'), lalr.Nonterm('States')]),
				lalr.Prod('States', 		[]),
				lalr.Prod('Block', 			[lalr.Term(TokenType.CURLY_LEFT), lalr.Nonterm('States'), lalr.Term(TokenType.CURLY_RIGHT)], action=lambda stack, userdata: userdata.__processBlock(stack[-3].attr.pos, stack[-1].attr.pos)),
				
				lalr.Prod('Type', 			[lalr.Nonterm('OptTypeModif'), lalr.Nonterm('TypeId'), lalr.Nonterm('OptTypePointer')]),
				lalr.Prod('Type', 			[lalr.Nonterm('TypeId'), lalr.Nonterm('OptTypePointer')]),
				lalr.Prod('TypeId', 		[lalr.Term(TokenType.ID)]),
				lalr.Prod('TypeId', 		[lalr.Term(TokenType.AUTO)]),
				lalr.Prod('TypeId', 		[lalr.Term(TokenType.BOOL)]),
				lalr.Prod('TypeId', 		[lalr.Term(TokenType.DOUBLE)]),
				lalr.Prod('TypeId', 		[lalr.Term(TokenType.FLOAT)]),
				lalr.Prod('TypeId', 		[lalr.Term(TokenType.INT)]),
				lalr.Prod('TypeId', 		[lalr.Term(TokenType.LONG)]),
				lalr.Prod('TypeId', 		[lalr.Term(TokenType.SHORT)]),
				lalr.Prod('TypeId', 		[lalr.Term(TokenType.VOID)]),
				lalr.Prod('OptTypeModif', 	[lalr.Term(TokenType.CONST), lalr.Nonterm('OptTypeModif')]),
				lalr.Prod('OptTypeModif', 	[]),
				lalr.Prod('OptTypePointer', [lalr.Term(TokenType.MULTIPLY), lalr.Nonterm('OptTypePointer')]),
				lalr.Prod('OptTypePointer', []),
				
				lalr.Prod('State', 			[lalr.Nonterm('Block')]),
				
				lalr.Prod('VarDef',			[lalr.Nonterm('Type'), lalr.Term(TokenType.ID), lalr.Nonterm('VarExtraDef'), lalr.Term(TokenType.TERMINATION_CHARACTER)], action=lambda stack, userdata: userdata.__registerId(stack[-3].attr)),
				lalr.Prod('VarDef',			[lalr.Nonterm('Type'), lalr.Term(TokenType.ID), lalr.Nonterm('VarExtraDef'), lalr.Term(TokenType.ASSIGN), lalr.Nonterm('Expr'), lalr.Term(TokenType.TERMINATION_CHARACTER)], action=lambda stack, userdata: userdata.__registerId(stack[-5].attr)),
				lalr.Prod('VarExtraDef',    [lalr.Term(TokenType.COMMA), lalr.Term(TokenType.ID), lalr.Nonterm('VarExtraDef')], action=lambda stack, userdata: userdata.__registerId(stack[-2].attr)),
				lalr.Prod('VarExtraDef',    []),

				lalr.Prod('FuncDef',		[lalr.Nonterm('Type'), lalr.Term(TokenType.ID), lalr.Term(TokenType.PARENTHESES_LEFT), lalr.Nonterm('FuncParams'), lalr.Term(TokenType.PARENTHESES_RIGHT), lalr.Term(TokenType.TERMINATION_CHARACTER)], action=lambda stack, userdata: userdata.__registerFunction(stack[-5].attr)),
				lalr.Prod('FuncDef',		[lalr.Nonterm('Type'), lalr.Term(TokenType.ID), lalr.Term(TokenType.PARENTHESES_LEFT), lalr.Nonterm('FuncParams'), lalr.Term(TokenType.PARENTHESES_RIGHT), lalr.Nonterm('Block')], action=lambda stack, userdata: userdata.__registerFunctionDef(stack[-5].attr, *stack[-1].attr)),
				lalr.Prod('FuncParams',		[lalr.Nonterm('FuncParam'), lalr.Nonterm('FuncParams\'')]),
				lalr.Prod('FuncParams',		[]),
				lalr.Prod('FuncParams\'',	[lalr.Term(TokenType.COMMA), lalr.Nonterm('FuncParams')]),
				lalr.Prod('FuncParams\'',	[]),
				lalr.Prod('FuncParam',		[lalr.Nonterm('Type'), lalr.Term(TokenType.ID)], action=lambda stack, userdata: userdata.__registerParameter(stack[-1].attr)),
				lalr.Prod('Macro',			[lalr.Term(TokenType.MACRO_INCLUDE)], action=lambda stack, userdata: userdata.__include(stack[-1].attr)),
				
				lalr.Prod('State',	[lalr.Nonterm('VarDef')]),
				lalr.Prod('State',	[lalr.Nonterm('FuncDef')]),
				lalr.Prod('State',	[lalr.Nonterm('Macro')]),
				lalr.Prod('State', 	[lalr.Term(TokenType.EXTERN), lalr.Term(TokenType.STRING), lalr.Nonterm('Block')]),
				lalr.Prod('State', 	[lalr.Term(TokenType.RETURN), lalr.Nonterm('Expr'), lalr.Term(TokenType.TERMINATION_CHARACTER)]),
				lalr.Prod('State', 	[lalr.Nonterm('Expr'), lalr.Term(TokenType.TERMINATION_CHARACTER)]),

				lalr.Prod('Primary', [lalr.Term(TokenType.ID)], action=lambda stack, userdata: userdata.__registerUsage(stack[-1].attr)),
				lalr.Prod('Primary', [lalr.Term(TokenType.NUMBER)]),
				lalr.Prod('Primary', [lalr.Term(TokenType.STRING)]),

				lalr.Prod('Expr', 	[lalr.Nonterm('Primary')]),
				lalr.Prod('Expr', 	[lalr.Term(TokenType.PARENTHESES_LEFT), lalr.Nonterm('Type'), lalr.Term(TokenType.PARENTHESES_RIGHT), lalr.Nonterm('Expr') ], operatorIndex=1),
				lalr.Prod('Expr',	[lalr.Term(TokenType.MULTIPLY), lalr.Nonterm('Expr')], operatorIndex=1),

				lalr.Prod('Expr',	[lalr.Nonterm('Expr'), lalr.Term(TokenType.ASSIGN), lalr.Nonterm('Expr')], operatorIndex=13)
			], range(TokenType.TOKEN_COUNT)
			, ['ltr', 'rtl', 'ltr', 'ltr', 'ltr', 'ltr', 'ltr', 'ltr', 'ltr', 'ltr', 'ltr', 'ltr', 'rtl', 'rtl', 'ltr' ]
			).buildParser(lambda token: token.type)

	def __init__(self, fileIndexTarget, ctags):
		self.fileIndexTarget = fileIndexTarget
		self.ctags = ctags

		self.parameters = []
		self.blocksStackEnds = []

		self.decls = {}
		self.usages = {}

	def lex(source):
		return Lexer(source).getTokens()

	def parse(self, tokens):
		Parser.__impl.parse(tokens, self)
		self.__flushDecl(0)
		for declId, usages in self.usages.items():
			self.fileIndexTarget._createDecl(declId, -1, -1, usages)
		self.usages.clear()

	def __flushDecl(self, beginPos, endPos=-1):
		declPoses = list(self.decls.keys())
		declPoses.sort(reverse=True)

		declPosesIndex = 0
		declPosesLen = len(declPoses)

		if endPos >= 0:
			while declPosesIndex < declPosesLen and declPoses[declPosesIndex] >= endPos:
				declPosesIndex += 1

		while declPosesIndex < declPosesLen and declPoses[declPosesIndex] >= beginPos:
			declBeginPos = declPoses[declPosesIndex]
			declId = self.decls[declBeginPos]
			del self.decls[declBeginPos]

			self.__postDecl(declId, declBeginPos, endPos)
			declPosesIndex += 1

	def __postDecl(self, declId, beginPos, endPos):
		if not declId in self.usages:
			self.fileIndexTarget._createDecl(declId, beginPos, endPos, set())
			return

		allUsagesSet = self.usages[declId]
		allUsages = list(allUsagesSet)
		allUsages.sort(reverse=True)

		usagesIndex = 0
		usagesLen = len(allUsages)

		if endPos >= 0:
			while usagesIndex < usagesLen and allUsages[usagesIndex] >= endPos:
				usagesIndex += 1

		usages = set()

		while usagesIndex < usagesLen and allUsages[usagesIndex] >= beginPos:
			usagePos = allUsages[usagesIndex]
			allUsagesSet.remove(usagePos)
			usages.add(usagePos)
			usagesIndex += 1

		self.fileIndexTarget._createDecl(declId, beginPos, endPos, set(usages))


	def __registerDecl(self, idName, pos):
		self.decls[pos] = idName

	def __include(self, filenameToken):
		self.fileIndexTarget._registerInclude(filenameToken.value, filenameToken.pos, self.ctags)

	def __processBlock(self, beginPos, endPos):
		self.__flushDecl(beginPos, endPos)
		return (beginPos, endPos)

	def __registerParameter(self, idToken):
		self.parameters.append(idToken)

	def __registerFunction(self, idToken):
		self.parameters.clear()
		self.__registerDecl(idToken.value, idToken.pos)

	def __registerFunctionDef(self, idToken, beginPos, endPos):
		self.__registerDecl(idToken.value, idToken.pos)
		for parameter in self.parameters:
			self.__postDecl(parameter.value, parameter.pos, endPos)
		self.parameters.clear()

	def __registerId(self, idToken):
		self.__registerDecl(idToken.value, idToken.pos)

	def __registerUsage(self, idToken):
		if idToken.value in self.usages:
			self.usages[idToken.value].append(idToken.pos)
		else:
			self.usages[idToken.value] = [idToken.pos]

class Decl:
	def __init__(self, idName, beginPos, endPos, usages):
		self.idName = idName
		self.beginPos = beginPos
		self.endPos = endPos
		self.usages = usages

	def fromDict(declDict):
		return Decl(declDict['idName'], declDict['beginPos'], declDict['endPos'], set(declDict['usages']))

	def toDict(self):
		return { 'idName' : self.idName,
		 'beginPos' : self.beginPos, 
		 'endPos' : self.endPos,
		 'usages' : list(self.usages) }

	def __hash__(self):
		return id(self)

	def __eq__(self, other):
		return self is other

	def __lt__(self, other):
		return self.beginPos < other.beginPos

class FileIndex:
	cacheCreationDate = 'creationDate'
	cacheIncludes = 'includes'
	cacheDecls = 'decls'
	cacheDeclsByPos = 'declsByPos'

	def __init__(self, filename):
		self.filename = filename
		self.creationDate = 0
		self.length = 0

		self.includes = {}
		self.decls = set()
		self.declsByPos = {}

		self.tokens = []

	def __resetDate(self):
		self.creationDate = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

	def __resetData(self):
		self.includes.clear()
		self.decls.clear()
		self.declsByPos.clear()

	def _registerInclude(self, filename, pos, ctags):
		pass

	def _createDecl(self, idName, beginPos, endPos, usages):
		decl = Decl(idName, beginPos, endPos, usages)
		self.decls.add(decl)
		self.declsByPos[beginPos] = decl
		for usage in usages:
			self.declsByPos[usage] = decl

	def toJson(self):
		declsList = list(self.decls)
		indicesOfDecls = { decl : index for index, decl in enumerate(declsList) }
		cache = {
			FileIndex.cacheCreationDate : self.creationDate,
		    FileIndex.cacheIncludes : self.includes,
		    FileIndex.cacheDecls : [decl.toDict() for decl in declsList],
		    FileIndex.cacheDeclsByPos : {pos : indicesOfDecls[decl] for pos, decl in self.declsByPos.items()}
		}
		return json.dumps(cache)

	def loadFromJson(filename, jsonStr):
		fileIndex = FileIndex(filename)
		cache = json.loads(jsonStr)

		if FileIndex.cacheCreationDate in cache:
			fileIndex.creationDate = int(cache[FileIndex.cacheCreationDate])
		if FileIndex.cacheIncludes in cache:
			fileIndex.includes = {int(k): v for k, v in cache[FileIndex.cacheIncludes].items()}
		if FileIndex.cacheDecls in cache and FileIndex.cacheDeclsByPos in cache:
			decls = [Decl.fromDict(declDict) for declDict in cache[FileIndex.cacheDecls]]
			fileIndex.decls = set(decls)
			fileIndex.declsByPos = {int(pos): decls[declIndex] for pos, declIndex in cache[FileIndex.cacheDeclsByPos].items()}

		return fileIndex

	def getPossibleIdsAt(self, ctags, pos, visited=set()):
		ids = set()

		for iPos, include in self.includes.items():
			if iPos < pos and not include in visited:
				visited.add(include)
				includedFileIndex = ctags.getFileIndex(include)
				ids.update(includedFileIndex.getPossibleIdsAt(ctags, includedFileIndex.length, visited))

		decls = list(self.decls)
		decls.sort()

		for decl in decls:
			if decl.beginPos > pos:
				break

			if decl.endPos < 0 or decl.endPos > pos:
				ids.add(decl.idName)

		return ids

	def getUsageFor(self, ctags, idName, pos, visited=set()):
		currentUsages = set()
		allUsages = { self.filename : currentUsages }

		if pos in self.declsByPos:
			decl = self.declsByPos[pos]

			currentUsages.add(decl.beginPos)
			currentUsages.update(decl.usages)

			if decl.beginPos >= 0:
				return allUsages

		for iPos, include in self.includes.items():
			if iPos < pos and not include in visited:
				visited.add(include)
				includedFileIndex = ctags.getFileIndex(include)
				allUsages.update(includedFileIndex.getUsageFor(ctags, idName, includedFileIndex.length, visited).items())

		return allUsages

	def __lexSource(self, source):
		try:
			tokens = Parser.lex(source)
			return tokens
		except Exception as e:
			raise Exception(f'{e} in file {self.filename}') from e

	def updateDecls(self, ctags):
		self.__resetData()
		parser = Parser(self, ctags)
		parser.parse(self.tokens)

	def fullUpdate(self, ctags):
		self.__resetDate()
		filecontent = None
		with open(ctags._fullFilename(self.filename), 'r', newline='') as sourceFile:
			filecontent = sourceFile.read()
		self.length = len(filecontent)
		self.tokens[:] = self.__lexSource(filecontent)

		self.updateDecls(ctags)

	def updateLine(self, ctags, fromPos, toPos, newLine):
		beginRemovedTokenIndex = bisect_left(self.tokens, fromPos, key=lambda token: token.pos)
		endRemovedTokenIndex = bisect_left(self.tokens, toPos, lo=beginRemovedTokenIndex, key=lambda token: token.pos)

		diff = fromPos + newLine - toPos
		for token in self.tokens[endRemovedTokenIndex:]:
			token.pos += diff
		
		self.tokens[beginRemovedTokenIndex:endRemovedTokenIndex] = self.__lexSource(newLine)

		self.updateDecls(ctags)

class CTags:
	indexCache = os.path.join('.ace', 'indices')

	def __init__(self, root):
		self.root = root
		self.indices = {}

	def getIncludeFileIndex(self, currentIndex, include):
		pass

	def _fullFilename(self, filename):
		return os.path.realpath(os.path.join(self.root, filename))

	def _cacheFilename(self, filename):
		return os.path.realpath(os.path.join(self.root, CTags.indexCache, filename + '.json'))

	def getFileIndex(self, filename):
		fileIndex = None

		fullFilename = self._fullFilename(filename)
		cacheFilename = self._cacheFilename(filename)

		if fullFilename in self.indices:
			fileIndex = self.indices[fullFilename]
		else:
			if os.path.isfile(cacheFilename):
				with open(cacheFilename, 'r') as jsonFile:
					fileIndex = FileIndex.loadFromJson(filename, jsonFile.read())

				if fileIndex.creationDate == 0:
					fileIndex.creationDate = os.path.getmtime(cacheFilename)
			else:
				fileIndex = FileIndex(filename)
			self.indices[filename] = fileIndex

		if fileIndex.creationDate < os.path.getmtime(fullFilename):
			fileIndex.fullUpdate(self)
			jsonStr = fileIndex.toJson()

			os.makedirs(os.path.dirname(cacheFilename), exist_ok=True)
			with open(cacheFilename, 'w') as jsonFile:
				jsonFile.write(jsonStr)
		return fileIndex

	def __lexLastId(source):
		offset = len(source) - 1
		lastId = False
		while offset >= 0:
			char = source[offset]
			if char.isnumeric():
				lastId = False
				offset -= 1
			elif char.isalpha() or char == '_':
				lastId = True
				offset -= 1
			else:
				break

		return source[offset + 1:] if lastId else ''

	def getIdProposeList(self, filename, pos, sourceLineBefore):
		lastId = CTags.__lexLastId(sourceLineBefore)
		if len(lastId) == 0:
			return []

		pos -= len(lastId)
		declarations = self.getFileIndex(filename).getPossibleIdsAt(self, pos)

		propositions = set()
		for keyword in _keywords:
			if keyword.startswith(lastId):
				propositions.add(keyword)
		for declaration in declarations:
			if declaration.startswith(lastId):
				propositions.add(declaration)

		if lastId in propositions:
			propositions.remove(lastId)

		propositionsCount = len(propositions)
		if propositionsCount <= 0:
			return []

		return [lastId] + list(propositions)

	def getIdUsageAtPosList(self, filename, pos, sourceLine, offset):
		lineLength = len(sourceLine)
		while offset < lineLength and (sourceLine[offset].isalnum() or sourceLine[offset] == '_'):
			pos += 1
			offset += 1

		lastId = CTags.__lexLastId(sourceLine[:offset])
		if len(lastId) == 0:
			return ['', {}]

		lastToken = Lexer.parseToken(lastId)
		if lastToken is None or lastToken.type != TokenType.ID:
			return ['', {}]

		pos -= len(lastId)
		usageDict = self.getFileIndex(filename).getUsageFor(self, lastId, pos)
		filteredUsageDict = {}
		for filename, usages in usageDict.items():
			if len(usages) > 0:
				listUsages = list(usages)
				listUsages.sort(reverse=True)
				filteredUsageDict[filename] = listUsages

		if len(filteredUsageDict) == 0:
			print(f'found nothing for {lastId} at {pos}')
		return [lastId, filteredUsageDict]

	def updateLine(self, filename, fromPos, toPos, newLine):
		self.getFileIndex(filename).updateLine(self, fromPos, toPos, newLine)

	def flushFile(self, filename):
		del self.indices[filename]

if __name__ == '__main__':
	root = 'C:\\Users\\Baton\\source\\repos\\ketljit'
	ctags = CTags(root)
	filename = '.\\src\\compiler\\lexer.c'
	fullFilename = os.path.realpath(os.path.join(root, filename))
	pos = 127
	print('Result', *ctags.parseAndPropose(fullFilename, pos, 'v'), sep=' ')