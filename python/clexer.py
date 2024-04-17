class TokenType:
	NUMBER 						= 0
	ID 							= 1
	STRING 						= 2
	CHAR 						= 3

	PARENTHESES_LEFT 			= 4 
	PARENTHESES_RIGHT 			= 5
	CURLY_LEFT 					= 6 
	CURLY_RIGHT 				= 7
	SQUARE_LEFT 				= 8 
	SQUARE_RIGHT 				= 9 
	DOT 						= 10
	POINTER 					= 11
	AMPERSAND 					= 12
	COMMA 						= 13
	TERNARY_FIRST 				= 14
	TERNARY_SECOND 				= 15
	TERMINATION_CHARACTER 		= 16

	LOGICAL_NOT 				= 17
	LOGICAL_AND					= 18
	LOGICAL_OR 					= 19
	LESS 						= 20
	LESS_OR_EQUAL 				= 21
	GREATER 					= 22
	GREATER_OR_EQUAL 			= 23
	EQUAL 						= 24
	NOT_EQUAL 					= 25

	BITWISE_NOT 				= 26
	BITWISE_AND 				= 27
	BITWISE_OR 					= 28
	BITWISE_XOR 				= 29
	BITWISE_SHIFT_LEFT 			= 30
	BITWISE_SHIFT_RIGHT			= 31

	INCREMENT					= 32
	DECREMENT					= 33
	PLUS 						= 34
	MINUS 						= 35
	MULTIPLY 					= 36
	DIVIDE 						= 37
	REMAINDER 					= 38

	ASSIGN 						= 39
	ASSIGN_PLUS 				= 40
	ASSIGN_MINUS 				= 41
	ASSIGN_MULTIPLY 			= 42
	ASSIGN_DIVIDE				= 43
	ASSIGN_REMAINDER 			= 44
	ASSIGN_BITWISE_SHIFT_LEFT 	= 45
	ASSIGN_BITWISE_SHIFT_RIGHT 	= 46
	ASSIGN_BITWISE_AND 			= 47
	ASSIGN_BITWISE_OR 			= 48
	ASSIGN_BITWISE_XOR 			= 49

	MACRO_DEFINE 				= 50
	MACRO_INCLUDE 				= 51

	AUTO 						= 52
	BOOL						= 53
	BREAK 						= 54
	CASE 						= 55
	CHAR 						= 56
	CONST 						= 57
	CONTINUE					= 58
	DEFAULT						= 59
	DO							= 60
	DOUBLE 						= 61
	ELSE 						= 62
	ENUM 						= 63
	EXTERN						= 64
	FALSE 						= 65
	FLOAT 						= 66
	FOR							= 67
	GOTO						= 68
	IF							= 69
	INLINE						= 70
	INT 						= 71
	LONG 						= 72
	REGISTER					= 73
	RETURN						= 74
	SHORT 						= 75
	SIGNED						= 76
	SIZEOF						= 77
	STATIC						= 78
	STRUCT						= 79
	SWITCH						= 80
	TRUE 						= 81
	TYPEDEF						= 82
	UNION						= 83
	UNSIGNED					= 84
	VOID						= 85
	VOLATILE					= 86
	WHILE						= 87

	TOKEN_COUNT					= 88
	ERROR 						= None


_operators = {
	'(': TokenType.PARENTHESES_LEFT, 
	')': TokenType.PARENTHESES_RIGHT,
	'{': TokenType.CURLY_LEFT,
	'}': TokenType.CURLY_RIGHT,
	'[': TokenType.SQUARE_LEFT, 
	']': TokenType.SQUARE_RIGHT, 
	'.': TokenType.DOT,
	'->': TokenType.POINTER,
	'&': TokenType.AMPERSAND,
	',': TokenType.COMMA,
	'?': TokenType.TERNARY_FIRST,
	':': TokenType.TERNARY_SECOND,
	';': TokenType.TERMINATION_CHARACTER,

	'!': TokenType.LOGICAL_NOT,
	'&&': TokenType.LOGICAL_AND,
	'||': TokenType.LOGICAL_OR,
	'<': TokenType.LESS,
	'<=': TokenType.LESS_OR_EQUAL,
	'>': TokenType.GREATER,
	'>=': TokenType.GREATER_OR_EQUAL,
	'==': TokenType.EQUAL,
	'!=': TokenType.NOT_EQUAL,

	'~': TokenType.BITWISE_NOT,
	'&': TokenType.BITWISE_AND,
	'|': TokenType.BITWISE_OR,
	'^': TokenType.BITWISE_XOR,
	'<<': TokenType.BITWISE_SHIFT_LEFT,
	'>>': TokenType.BITWISE_SHIFT_RIGHT,

	'++': TokenType.INCREMENT,
	'--': TokenType.DECREMENT,
	'+': TokenType.PLUS,
	'-': TokenType.MINUS,
	'*': TokenType.MULTIPLY,
	'/': TokenType.DIVIDE,
	'%': TokenType.REMAINDER,

	'=': TokenType.ASSIGN,
	'+=': TokenType.ASSIGN_PLUS,
	'-=': TokenType.ASSIGN_MINUS,
	'*=': TokenType.ASSIGN_MULTIPLY,
	'/=': TokenType.ASSIGN_DIVIDE,
	'%=': TokenType.ASSIGN_REMAINDER,
	'<<=': TokenType.ASSIGN_BITWISE_SHIFT_LEFT,
	'>>=': TokenType.ASSIGN_BITWISE_SHIFT_RIGHT,
	'&=': TokenType.ASSIGN_BITWISE_AND,
	'|=': TokenType.ASSIGN_BITWISE_OR,
	'^=': TokenType.ASSIGN_BITWISE_XOR
	}
_keywords = {
	'auto': TokenType.AUTO,
	'bool': TokenType.BOOL,
	'break': TokenType.BREAK,
	'case': TokenType.CASE,
	'const': TokenType.CONST,
	'continue': TokenType.CONTINUE,
	'default': TokenType.DEFAULT,
	'do': TokenType.DO,
	'double': TokenType.DOUBLE,
	'else': TokenType.ELSE,
	'enum': TokenType.ENUM,
	'extern': TokenType.EXTERN,
	'false': TokenType.FALSE,
	'float': TokenType.FLOAT,
	'for': TokenType.FOR,
	'goto': TokenType.GOTO,
	'if': TokenType.IF,
	'inline': TokenType.INLINE,
	'int': TokenType.INT,
	'long': TokenType.LONG,
	'register': TokenType.REGISTER,
	'return': TokenType.RETURN,
	'short': TokenType.SHORT,
	'signed': TokenType.SIGNED,
	'sizeof': TokenType.SIZEOF,
	'static': TokenType.STATIC,
	'struct': TokenType.STRUCT,
	'switch': TokenType.SWITCH,
	'true': TokenType.TRUE,
	'typedef': TokenType.TYPEDEF,
	'union': TokenType.UNION,
	'unsigned': TokenType.UNSIGNED,
	'void': TokenType.VOID,
	'volatile': TokenType.VOLATILE,
	'while': TokenType.WHILE
	}

class Token:
	def __init__(self, type, value, pos):
		self.type = type
		self.value = value
		self.pos = pos

	def __repr__(self):
		return f'Token({self.type}, \'{self.value}\' at {self.pos})'

	def num(value, pos):
		return Token(TokenType.NUMBER, value, pos)

	def id(value, pos):
		return Token(_keywords[value] if value in _keywords else TokenType.ID, value, pos)

	def str(value, pos):
		return Token(TokenType.STRING, value, pos)

	def char(value, pos):
		return Token(TokenType.CHAR, value, pos)

	def macroInclude(value, pos):
		return Token(TokenType.MACRO_INCLUDE, value, pos)

	def macro(value, pos):
		return Token(None, value, pos)

	def op(value, pos):
		if value not in _operators:
			raise Exception(f'Unknown operator "{value}" ({value.encode("utf-8")}) at {pos}')
		return Token(_operators[value], value, pos)

class Lexer:
	twoCharOps = set([
			"++", "--",
			"->",
			"<<", ">>",
			"<=", ">=",
			"==", "!=",
			"&&", "||", 
			"+=", "-=",
			"*=", "/=", "%=",
			"&=", "^=", "|="
		])

	firstCharTwoCharOps = set((op[0] for op in twoCharOps))

	def __init__(self, source):
		self.tokens = []
		self.offset = 0
		self.source = source
		self.length = len(source)

		self.char = None

		self.__parse()

	def parseToken(source):
		tokens = Lexer(source).getTokens()
		if len(tokens) != 1:
			return None
		return tokens[0]

	def __readChar(self):
		self.char = self.source[self.offset] if self.offset < self.length else ''

	def __parseComments(self):
		if self.char != '/' or self.offset + 1 >= self.length:
			return False

		nextChar = self.source[self.offset + 1]

		# one line comment
		if nextChar == '/':
			self.offset += 2
			self.__skipUntilNextLine()
			return True

		# multiline comment
		if nextChar == '*':
			self.offset += 2
			while self.offset < self.length:
				nextChar = self.source[self.offset]

				if nextChar == '*' and self.offset + 1 < self.length and self.source[self.offset + 1] == '/':
					self.offset += 2
					break

				self.offset += 1
			#else:
				# error

			return True

		return False

	def __parseNextLine(self):
		if self.char == '\r':
			if self.offset + 1 < self.length and self.source[self.offset + 1] == '\n':
				self.offset += 2
			else:
				self.offset += 1
			return True

		if self.char == '\n':
			self.offset += 1
			return True

		return False

	def __skipUntilNextLine(self):
		while self.offset < self.length:
			self.__readChar()
			if self.__parseNextLine():
				break
			self.offset += 1

	def __parseChar(self):
		if self.char != '\'':
			return False

		# error correction
		if self.offset + 2 >= self.length or self.source[self.offset + 2] != '\'':
			char = self.offset + 1 < self.length if self.source[self.offset + 1] else ''
			self.tokens.append(Token.char(char, self.offset + 1))
			return True

		self.tokens.append(Token.char(self.source[self.offset + 1], self.offset + 1))
		self.offset += 2
		return True

	def __parseString(self):
		if self.char != '"':
			return False

		self.offset += 1
		initialOffset = self.offset
		while self.offset < self.length and self.source[self.offset] != '"':
			self.offset += 1

		#if offset >= length:
			#error

		self.tokens.append(Token.str(self.source[initialOffset:self.offset], initialOffset))
		self.offset += 1
		return True

	def __parseMacro(self):
		if self.char != '#':
			return False

		self.offset += 1
		includeStr = 'include'
		includeStrLen = len(includeStr)
		if self.offset + includeStrLen <= self.length and self.source[self.offset:self.offset + includeStrLen] == includeStr:
			self.offset += includeStrLen

			self.__readChar()
			while self.char != '' and self.char != '"' and self.char != '<' and self.char != '\n':
				self.offset += 1
				self.__readChar()

			if self.char == '' or self.char == '\n':
				# error
				return True

			self.offset += 1
			initialOffset = self.offset

			self.__readChar()
			while self.char != '' and self.char != '"' and self.char != '>' and self.char != '\n':
				self.offset += 1
				self.__readChar()

			if self.char == '' or self.char == '\n':
				# error
				return True

			self.tokens.append(Token.macroInclude(self.source[initialOffset:self.offset], initialOffset))

			self.__skipUntilNextLine()
			return True
		
		return False

	def __parseNumber(self):
		if not self.char.isnumeric():
			return False

		initialOffset = self.offset
		self.offset += 1

		self.__readChar()
		while self.char.isnumeric():
			self.offset += 1
			self.__readChar()

		self.tokens.append(Token.num(self.source[initialOffset:self.offset], initialOffset))
		return True

	def __parseId(self):
		if not self.char.isalpha() and self.char != '_':
			return False

		initialOffset = self.offset
		self.offset += 1

		self.__readChar()
		while self.char.isalnum() or self.char == '_':
			self.offset += 1
			self.__readChar()

		self.tokens.append(Token.id(self.source[initialOffset:self.offset], initialOffset))
		return True

	def __parseOp(self):
		if self.char in Lexer.firstCharTwoCharOps and self.offset + 1 < self.length and self.source[self.offset:self.offset + 2] in Lexer.twoCharOps:
			nextChar = self.source[self.offset + 1]
			# three character op
			if (nextChar == '<' or nextChar == '>') and self.offset + 2 < self.length and self.source[self.offset + 2] == '=':
				self.tokens.append(Token.op(self.source[self.offset:self.offset + 3], self.offset))
				self.offset += 3
			else:
				self.tokens.append(Token.op(self.source[self.offset:self.offset + 2], self.offset))
				self.offset += 2
			return True

		self.tokens.append(Token.op(self.char, self.offset))
		self.offset += 1

		return True

	def __parse(self):
		while True:
			self.__readChar()

			if self.char == '':
				break

			if self.__parseNextLine():
				continue

			# whitespace
			if self.char.isspace():
				self.offset += 1
				continue

			if self.__parseComments():
				continue

			if self.__parseChar():
				continue

			if self.__parseString():
				continue

			if self.__parseMacro():
				continue

			if self.__parseNumber():
				continue

			if self.__parseId():
				continue

			if self.__parseOp():
				continue

			break

	def getTokens(self):
		return self.tokens[:]