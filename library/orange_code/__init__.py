'''
    orange_code_terminal_v1.py; orange_code version 1, a very early version, is capable of running basic orange_code programs.
    Copyright (C) 2017  Sam Alws

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


#This program can run orange_code programs in the terminal.

####SETUP####
import time
import re
####UTILITY FUNCTIONS####
def error(msg):
	raise Exception(msg) #improve this later
def getCountFunction(string,counter):
	return string.count(counter)-string.count('\\'+counter)
def getNextExpression(code,location):
	currentLocation=location
	while True:
		nextSemi=code.find(';',currentLocation)
		nextComma=code.find(',',currentLocation)
		nextLoc=nextComma if (nextComma!=-1 and (nextComma<nextSemi or nextSemi==-1)) else nextSemi
		
		nextCodeChunk=code[location:nextLoc]
		if nextLoc==-1:
			return (code[location:],',',-1)
		elif code[nextLoc-1]=='\\':
			currentLocation=nextLoc+1
		elif getCountFunction(nextCodeChunk,'(')!=getCountFunction(nextCodeChunk,')') or getCountFunction(nextCodeChunk,'[')!=getCountFunction(nextCodeChunk,']') or getCountFunction(nextCodeChunk,'{')!=getCountFunction(nextCodeChunk,'}'):
			currentLocation=nextLoc+1
		elif getCountFunction(nextCodeChunk,'"')%2!=0 or getCountFunction(nextCodeChunk,"'")%2!=0:
			currentLocation=nextLoc+1
		else:
			return (nextCodeChunk,code[nextLoc],nextLoc+1)
orderOfOperations0=['=','~','**','//','*','/','%','+','-','&','|','!&','!|','>','<','!']
orderOfOperations=list(orderOfOperations0)
#generate x= and x== where x is all the previous characters
for loc in range(16):
	orderOfOperations.insert(2,orderOfOperations0[15-loc]+'=')
for loc in range(16):
	orderOfOperations.insert(2,orderOfOperations0[15-loc]+'==')
#move the ! to the end, add `. and `#
orderOfOperations.remove('!')
orderOfOperations.append('`#')
orderOfOperations.append('`.')
orderOfOperations.append('!')
def tuplizeExpression(expression): #breaks a string expression into its tuple of its parts
	specialCharacters=['~','`','!','%','&','*','-','+','=','|','<','>','/']
	correspondingCharacters={'(':')','{':'}','[':']','"':'"','\'':'\''}
	returnValue=[expression[0]] #start as a list bc tuples are annoying to work with
	for char in expression[1:]:
		topReturnValue = returnValue[len(returnValue)-1]
		firstCharacter=topReturnValue[0]
		if firstCharacter in correspondingCharacters: #(asdf), [asdf], "asdf", etc
			#first off, is it done yet?
			amountOfStarter=topReturnValue.count(firstCharacter)
			amountOfStarter-=topReturnValue.count("\\"+firstCharacter)
			isDone = False
			#find out in different ways based on whether the start and finishing characters are the same (eg "")
			#or if they're different (eg [])
			correspondingCharacter=correspondingCharacters[firstCharacter]
			if correspondingCharacter==firstCharacter:
				isDone=(amountOfStarter>1)
			else:
				amountOfEnder=topReturnValue.count(correspondingCharacter)
				amountOfEnder-=topReturnValue.count("\\"+correspondingCharacter)
				if amountOfStarter==amountOfEnder:
					isDone=True
			#if done, add another element; otherwise, continue on with this element
			if isDone:
				returnValue.append(char)
			else:
				returnValue[len(returnValue)-1]+=char
		elif char!=' ' and char!='\t' and char!='\n':
			if firstCharacter in specialCharacters:
				if char in specialCharacters:
					returnValue[len(returnValue)-1]+=char
				elif topReturnValue=='`' and (char=='.' or char=='#'):
					returnValue[len(returnValue)-1]+=char
				else:
					if len(topReturnValue)>1 and topReturnValue[-1]=='!':
						returnValue.insert(-1,topReturnValue[:-1])
						returnValue[-1]='!'
						topReturnValue=topReturnValue[:-1]
					if not topReturnValue in orderOfOperations:
						error(topReturnValue+" is not a valid operator.")
					returnValue.append(char)
			else:
				if char in specialCharacters or char in correspondingCharacters:
					returnValue.append(char)
				else:
					returnValue[len(returnValue)-1]+=char
	return tuple(returnValue)
def split(table,splitter,isPrefix):
	#only accepts tables of length 2 or more
	#when isPrefix is True: ['!a','',''] -> [['a','none','!'],'','']
	#when isPrefix is False (infix): ['a~a~a','',''] -> [['a',['a','a','~'],'~'],'','']
	for location in range(2):
		element=table[location]
		if type(element) is tuple:
			if splitter in element:
				locInTup=element.index(splitter)
				if isPrefix:
					if locInTup==0:
						table[location]=split([element[1:],('none',),splitter],splitter,isPrefix)
					else:
						error('Malformed expression.')
				else:
					if locInTup==0:
						error('Malformed expression.')
					table[location]=split([element[:locInTup],element[locInTup+1:],splitter],splitter,isPrefix)
		else:
			table[location]=split(element,splitter,isPrefix)
	return table
def detuplize(table): #takes a table made in the split function; turns all tuples, each of which which contains 1 string, into the strings
	for location in range(2):
		if type(table[location]) is tuple:
			table[location]=table[location][0]
		else:
			table[location]=detuplize(table[location])
	return table
	
def processExpression(expression):
	#turn it into a tuple of its parts
	expression=tuplizeExpression(expression)
	if len(expression)==1:
		return expression[0]
	#now apply order of operations
	isPrefix={'!':True}
	table=[expression,()] #split only accepts tables of length 2 or more
	for splitter in orderOfOperations:
		table = split(table,splitter,splitter in isPrefix)
	return detuplize(table[0])
def nextProcessedExpression(code,location):
	(expression,ending,nextLocation)=getNextExpression(code,location)
	return (processExpression(expression),ending,nextLocation)
stringReplacements={'`':'backtick','~':'tilde','!':'exclamation','#':'hashtag','%':'percent','&':'and','*':'asterisk','-':'minus','+':'plus','=':'equal','.':'period','/':'slash','<':'less','>':'greater','|':'pipe'}
def fixString(string):
	for replace,replaceWith in stringReplacements.items():
		string=string.replace(replace,replaceWith)
	return string
####CODEOBJ####
defaultVariables=[]  #entries are added below
returnedValue=False
class codeObj:
	code=''
	variables=[]
	creator=None
	def __init__(self,creator=None):
		self.variables=list(defaultVariables) #clones defaultVariables
		self.creator=creator
	def __append(self,obj):
		#first check what element to put it in
		elemNum=0.0
		while True: #could result in infinite loop if you add an element that makes getVal always return it, whoops
			if type(self.getVal(numObj(elemNum),False)) is noneObj:
				break
			elemNum+=1
		self.setVal(numObj(elemNum,self),obj)
	def __evaluate(self,obj):
		if type(obj) is str:
			return self.getString(obj)
		else:
			element0=self.__evaluate(obj[0])
			element1=self.__evaluate(obj[1])
			return element0.getVal(strObj(fixString(obj[2]))).run(element1,element0)
	def removeVal(self,index):
		for entry in self.variables:
			isEqual = entry[0].getVal(strObj('equalequal')).run(index,entry[0])
			if isEqual.getVal(strObj('cast')).run(strObj('boolean'),isEqual).value:
				self.variables.remove(entry)
				self.removeVal(index)
				break
	def setVal(self,index,value,removeFirst=True):
		if removeFirst:
			self.removeVal(index)
		self.variables.append((index,value))
	def getVal(self,index,callOtherFunc=True):
		for entry in self.variables:
			isEqual = entry[0].getVal(strObj('equalequal')).run(index,entry[0])
			if isEqual.getVal(strObj('cast')).run(strObj('boolean'),isEqual).value:
				if type(entry[1]) is functionObj:
					entry[1].creator=self #really hacky bugfix :)
				return entry[1]
		return noneObj()
	@staticmethod
	def __takeOutFirstCharacter(a):
		return a.group(0)[1:]
	def getString(self,string):
		if string[0]=='"' or string[0]=="'":
			return strObj(re.sub('\\\\.',self.__takeOutFirstCharacter,string[1:-1].replace('\\n','\n').replace('\\t','\t')),self)
		elif string[0]=='(':
			newObj=codeObj(self)
			newObj.code=string[1:-1]
			newObj.run(noneObj(),self)
			return newObj.getVal(numObj(0.0,self))
		elif string[0]=='[':
			newObj=codeObj(self)
			newObj.code=string[1:-1]
			newObj.run(noneObj(),self)
			return newObj
		elif string[0]=='{':
			newObj=codeObj(self)
			newObj.code=string[1:-1]
			return newObj
		
		nextDelimeter=string.find('.',1)
		nextDelimeter=string.find('#',1) if (string.find('#',1)!=-1 and (string.find('#',1)<nextDelimeter or nextDelimeter==-1)) else nextDelimeter
		thisElement=string[1:nextDelimeter] if nextDelimeter!=-1 else string[1:]
		if string[0]!='#' and string[0]!='.':
			thisElement=string[0]+thisElement
		nextElement=string[nextDelimeter:] if nextDelimeter!=-1 else ''
		
		obj=None #will set below
		try:
			int(thisElement)
			isInt=True
		except ValueError:
			isInt=False
		
		if isInt and (string[0]!='#' and string[0]!='.'):
			obj=numObj(float(thisElement),self)
			
			if nextElement!='' and nextElement[0]=='.':
				nextDelimeter2=nextElement.find('.',1)
				nextDelimeter2=nextElement.find('#',1) if (nextElement.find('#',1)!=-1 and (nextElement.find('#',1)<nextDelimeter2 or nextDelimeter2==-1)) else nextDelimeter2
				thisElement2=nextElement[1:nextDelimeter2] if nextDelimeter2!=-1 else nextElement[1:]
				try:
					int(thisElement2)
					isInt2=True
				except ValueError:
					isInt2=False
				if isInt2:
					obj=numObj(float(thisElement+'.'+thisElement2),self)
					nextElement=nextElement[nextDelimeter2:] if nextDelimeter2!=-1 else ''
		elif thisElement.count('$')==len(thisElement):
			obj=self
			for _ in range(thisElement.count('$')-1):
				if obj.creator:
					obj=obj.creator
				else:
					break
		elif string[0]=='#':
			obj=ptrObj(self,numObj(float(thisElement),self) if isInt else strObj(thisElement,self),self)
		else:
			obj=self.getVal(numObj(float(thisElement),self) if isInt else strObj(thisElement,self))
		if nextElement=='':
			return obj
		else:
			return obj.getString(nextElement)
	def run(self,arg,_=None):
		global returnedValue
		returnedValue=False
		self.setVal(strObj('@'),arg)
		location=0
		while location!=-1 and location<len(self.code):
			(expression,ender,location)=nextProcessedExpression(self.code,location)
			finalVal=self.__evaluate(expression)
			if returnedValue:
				a=returnedValue
				returnedValue=False
				return a
			if ender==',':
				self.__append(finalVal)
		return noneObj()
####BASIC OBJECTS####]
#value
def valueEqualEqual(_,arg,creator):
	if type(arg) is type(creator):
		return booleanObj(creator.value==arg.value)
	else:
		return booleanObj(creator is arg)
def valueGreater(_,arg,creator):
	if type(arg) is type(creator):
		return booleanObj(creator.value>arg.value)
	else:
		return booleanObj(creator is arg)
def valueLess(_,arg,creator):
	if type(arg) is type(creator):
		return booleanObj(creator.value<arg.value)
	else:
		return booleanObj(creator is arg)
presetStrObjs={} #annoying bugfix to prevent infinite recursion; continued later on in the code
class valueObj(codeObj):
	value=None
	datatype=None
	def __init__(self,value,creator=None):
		super().__init__(creator)
		if not type(value) is self.datatype:
			error("Type mismatch.")
		self.value=value
		self.variables[0]=(self.variables[0][0],functionObj(valueEqualEqual,self))
		self.variables.append((presetStrObjs['greater'],functionObj(valueGreater,self)))
		self.variables.append((presetStrObjs['less'],functionObj(valueLess,self)))
#number
def numCast(_,arg,creator):
	if not type(arg) is strObj:
		return creator
	if arg.value=='boolean':
		return booleanObj(creator.value!=0)
	if arg.value=='string':
		if int(creator.value)==creator.value:
			return strObj(str(int(creator.value)))
		else:
			return strObj(str(creator.value))
	if arg.value=='number':
		return creator
def numPlus(_,arg,creator):
	casted=arg.getString('cast').run(strObj('number'),arg)
	if type(casted) is numObj:
		return numObj(creator.value+arg.value)
	else:
		return noneObj()
def numMinus(_,arg,creator):
	casted=arg.getString('cast').run(strObj('number'),arg)
	if type(casted) is numObj:
		return numObj(creator.value-arg.value)
	else:
		return noneObj()
def numAsterisk(_,arg,creator):
	casted=arg.getString('cast').run(strObj('number'),arg)
	if type(casted) is numObj:
		return numObj(creator.value*arg.value)
	else:
		return noneObj()
def numSlash(_,arg,creator):
	casted=arg.getString('cast').run(strObj('number'),arg)
	if type(casted) is numObj:
		return numObj(creator.value/arg.value)
	else:
		return noneObj()
def numAsteriskAsterisk(_,arg,creator):
	casted=arg.getString('cast').run(strObj('number'),arg)
	if type(casted) is numObj:
		return numObj(creator.value**arg.value)
	else:
		return noneObj()
def numSlashSlash(_,arg,creator):
	casted=arg.getString('cast').run(strObj('number'),arg)
	if type(casted) is numObj:
		return numObj(creator.value//arg.value)
	else:
		return noneObj()
def numPercent(_,arg,creator):
	casted=arg.getString('cast').run(strObj('number'),arg)
	if type(casted) is numObj:
		return numObj(creator.value%arg.value)
	else:
		return noneObj()
def numExclamation(_,__,creator):
	return numObj(-1*creator.value)
class numObj(valueObj):
	datatype=float
	def __init__(self,value,creator=None):
		super().__init__(value,creator)
		self.variables.append((strObj('plus'),functionObj(numPlus,self)))
		self.variables.append((strObj('minus'),functionObj(numMinus,self)))
		self.variables.append((strObj('asterisk'),functionObj(numAsterisk,self)))
		self.variables.append((strObj('slash'),functionObj(numSlash,self)))
		self.variables.append((strObj('asteriskasterisk'),functionObj(numAsteriskAsterisk,self)))
		self.variables.append((strObj('slashslash'),functionObj(numSlashSlash,self)))
		self.variables.append((strObj('percent'),functionObj(numPercent,self)))
		self.variables.append((strObj('exclamation'),functionObj(numExclamation,self)))
		self.variables[1]=(self.variables[1][0],functionObj(numCast,self))
#string
def strCast(_,arg,creator):
	if not type(arg) is strObj:
		return creator
	if arg.value=='boolean':
		return booleanObj(True)
	if arg.value=='string':
		return creator
	if arg.value=='number':
		try:
			return numObj(float(creator.value))
		except ValueError:
			return numObj(0.0)
def strPlus(_,arg,creator):
	if type(arg) is strObj:
		return strObj(creator.value+arg.value)
	else:
		return noneObj()
def strMinus(_,arg,creator):
	if type(arg) is strObj:
		return strObj(creator.value.replace(arg.value,''))
	else:
		return noneObj()
def strAsterisk(_,arg,creator):
	if type(arg) is numObj:
		return strObj(creator.value*int(arg.value))
	else:
		element0=arg.getVal(numObj(0.0))
		element1=arg.getVal(numObj(1.0))
		if type(element0) is strObj and type(element1) is strObj:
			return strObj(creator.value.replace(element0.value,element1.value))
		else:
			return noneObj()
def strSlash(_,arg,creator):
	if type(arg) is strObj:
		return numObj(float(creator.value.find(arg.value)))
	else:
		return noneObj()
def strAsteriskAsterisk(_,__,creator):
	return strObj(creator.value.upper())
def strSlashSlash(_,__,creator):
	return strObj(creator.value.lower())
def strPercent(_,arg,creator):
	if type(arg) is strObj:
		return numObj(float(creator.value.count(arg.value)))
	else:
		return noneObj()
class strObj(valueObj):
	datatype=str
	def __init__(self,value,creator=None,beforeStartup=False):
		if not beforeStartup:
			super().__init__(value,creator)
			self.variables.append((presetStrObjs['plus'],functionObj(strPlus,self)))
			self.variables.append((presetStrObjs['minus'],functionObj(strMinus,self)))
			self.variables.append((presetStrObjs['asterisk'],functionObj(strAsterisk,self)))
			self.variables.append((presetStrObjs['slash'],functionObj(strSlash,self)))
			self.variables.append((presetStrObjs['asteriskasterisk'],functionObj(strAsteriskAsterisk,self)))
			self.variables.append((presetStrObjs['slashslash'],functionObj(strSlashSlash,self)))
			self.variables.append((presetStrObjs['percent'],functionObj(strPercent,self)))
			self.variables[1]=(self.variables[1][0],functionObj(strCast,self))
		else:
			self.value=value

	#below: equalequal is modifiable but defaults to the normal == function while avoiding infinite loops
	equalEqualChanged=False
	def getVal(self,index,callOtherFunc=True): #to avoid infinte loops
		if not self.equalEqualChanged and type(index) is strObj and index.value=='equalequal':
			return self.variables[0][1]
		else:
			return super().getVal(index)
	def setVal(self,index,value,removeFirst=True):
		if not self.equalEqualChanged and type(index) is strObj and index.value=='equalequal':
			self.equalEqualChanged=True
		super().setVal(index,value,removeFirst=True)
def addToPresetStrObjs(stringVal):
	presetStrObjs[stringVal]=strObj(stringVal,None,True)
for string in ['plus','minus','asterisk','slash','asteriskasterisk','slashslash','percent','greater','less']:
	addToPresetStrObjs(string)
#boolean
def booleanCast(_,arg,creator):
	if not type(arg) is strObj:
		return creator
	if arg.value=='boolean':
		return creator
	if arg.value=='string':
		return strObj('true') if creator.value else strObj('false')
	if arg.value=='number':
		return numObj(1.0) if creator.value else numObj(0.0)
class booleanObj(valueObj):
	datatype=bool
	def __init__(self,value,creator=None):
		super().__init__(value,creator)
		self.variables[1]=(self.variables[1][0],functionObj(booleanCast,self))
	#below: cast is modifiable but defaults to the normal cast function while avoiding infinite loops
	equalEqualChanged=False
	def getVal(self,index,callOtherFunc=True): #to avoid infinte loops
		if not self.equalEqualChanged and type(index) is strObj and index.value=='cast':
			return self.variables[1][1]
		else:
			return super().getVal(index,callOtherFunc)
	def setVal(self,index,value,removeFirst=True):
		if not self.equalEqualChanged and type(index) is strObj and index.value=='cast':
			self.equalEqualChanged=True
		super().setVal(index,value,removeFirst=True)
#pointer
def ptrEqual(_,arg,creator):
	creator.obj.setVal(creator.index,arg)
	return noneObj()
def ptrXEqual(self,arg,creator):
	obj=creator.obj.getVal(creator.index)
	creator.obj.setVal(creator.index,obj.getString(fixString(self.optionalArgument)).run(arg,obj))
	return noneObj()
class ptrObj(codeObj):
	def __init__(self,obj,index,creator=None):
		super().__init__(creator)
		self.setVal(strObj('obj'),obj)
		self.setVal(strObj('index'),index)
		self.obj=obj
		self.index=index
		self.variables.append((strObj('equal'),functionObj(ptrEqual,self)))
		self.variables.append((strObj('tildeequal'),functionObj(ptrXEqual,self,'~')))
		self.variables.append((strObj('asteriskasteriskequal'),functionObj(ptrXEqual,self,'**')))
		self.variables.append((strObj('slashslashequal'),functionObj(ptrXEqual,self,'//')))
		self.variables.append((strObj('asteriskequal'),functionObj(ptrXEqual,self,'*')))
		self.variables.append((strObj('slashequal'),functionObj(ptrXEqual,self,'/')))
		self.variables.append((strObj('percentequal'),functionObj(ptrXEqual,self,'%')))
		self.variables.append((strObj('plusequal'),functionObj(ptrXEqual,self,'+')))
		self.variables.append((strObj('minusequal'),functionObj(ptrXEqual,self,'-')))
		self.variables.append((strObj('andequal'),functionObj(ptrXEqual,self,'&')))
		self.variables.append((strObj('pipeequal'),functionObj(ptrXEqual,self,'|')))
		self.variables.append((strObj('exclamationandequal'),functionObj(ptrXEqual,self,'!&')))
		self.variables.append((strObj('exclamationpipeequal'),functionObj(ptrXEqual,self,'!|')))
		self.variables.append((strObj('greaterequal'),functionObj(ptrXEqual,self,'>')))
		self.variables.append((strObj('lessequal'),functionObj(ptrXEqual,self,'<')))
		self.variables.append((strObj('exclamationequal'),functionObj(ptrXEqual,self,'!')))
#function
class functionObj(codeObj):
	func=None
	code='[coded in python]'
	def __init__(self,func,creator=None,optionalArgument=None):
		super().__init__(creator)
		self.func=func
		self.optionalArgument=optionalArgument
	def run(self,arg,optionalArgument=None):
		return self.func(self,arg,optionalArgument)
#none
def noneCast(_,arg,creator):
	if not type(arg) is strObj:
		return creator
	if arg.value=='boolean':
		return booleanObj(False)
	if arg.value=='string':
		return strObj('none')
	if arg.value=='number':
		return numObj(0.0)
class noneObj(codeObj):
	def __init__(self,creator=None):
		super().__init__(creator)
		self.variables[1]=(self.variables[1][0],functionObj(noneCast,self))
####BASIC FUNCTIONS####
def equalequal(_,arg,creator):
	return booleanObj(creator is arg)
def tilde(_,arg,creator):
	return creator.run(arg,creator.creator)
def backtickperiod(_,arg,creator):
	return creator.getVal(arg)
def backtickhashtag(_,arg,creator):
	return ptrObj(creator,arg,creator)
def Not(_,__,creator):
	casted=creator.getString('cast').run(strObj('boolean'),creator)
	if type(casted) is booleanObj:
		return booleanObj(not casted.value,creator)
	else:
		return booleanObj(True,creator)
def exclamationequal(_,arg,creator):
	return Not(None,None,creator.getString('equalequal').run(arg,creator))
def greaterequal(_,arg,creator):
	return Not(None,None,creator.getString('less').run(arg,creator))
def lessequal(_,arg,creator):
	return Not(None,None,creator.getString('greater').run(arg,creator))
def And(_,arg,creator):
	casted=creator.getString('cast').run(strObj('boolean'),creator)
	if type(casted) is booleanObj:
		if casted.value:
			return arg
		else:
			return creator
	else:
		return noneObj()
def Or(_,arg,creator):
	casted=creator.getString('cast').run(strObj('boolean'),arg)
	if type(casted) is booleanObj:
		if casted.value:
			return creator
		else:
			return arg
	else:
		return noneObj()
def nand(_,arg,creator):
	return Not(None,None,And(_,arg,creator))
def nor(_,arg,creator):
	return Not(None,None,Or(_,arg,creator))
def cast(_,arg,creator):
	if type(arg) is strObj and arg.value=='boolean':
		return booleanObj(True)
	else:
		return creator
def Print(_,arg,__):
	casted=arg.getString('cast').run(strObj('string'),arg)
	if type(casted) is strObj:
		print(casted.value,end='')
	return noneObj()
def Println(_,arg,__):
	casted=arg.getString('cast').run(strObj('string'),arg)
	if type(casted) is strObj:
		print(casted.value)
	return noneObj()
def wait(_,arg,__):
	casted=arg.getString('cast').run(strObj('number'),arg)
	if type(casted) is numObj:
		time.sleep(casted.value)
	return noneObj()
def If(_,arg,__):
	condition=arg.getVal(numObj(0.0)).getString('cast').run(strObj('boolean'),arg.getVal(numObj(0.0)))
	if type(condition) is booleanObj and condition.value:
		arg.getVal(numObj(1.0)).run(noneObj)
	return noneObj()
def While(_,arg,__):
	while True:
		condition=arg.getVal(numObj(0.0)).getString('cast').run(strObj('boolean'),arg.getVal(numObj(0.0)))
		if type(condition) is booleanObj and condition.value:
			arg.getVal(numObj(1.0)).run(noneObj)
		else:
			return noneObj()
def For(_,arg,creator):
	location=0.0
	while True:
		element=arg.getVal(numObj(0.0)).getVal(numObj(location))
		if type(element) is not noneObj:
			arg.getVal(numObj(1.0)).run(element,creator)
		else:
			return noneObj()
		location+=1
def Return(_,arg,__):
	global returnedValue
	returnedValue=arg
def Len(_,__,creator):
	location=0.0
	while True:
		if type(creator.getVal(numObj(location))) is noneObj:
			return numObj(location,creator)
		location+=1
def Input(_,__,creator):
	return strObj(input(),creator)
def Assert(_,arg,__):
	condition=arg.getString('cast').run(strObj('boolean'),arg)
	if not(type(condition) is booleanObj and condition.value):
		error('Assertation failed.')
	return noneObj()
defaultVariables.append((strObj('equalequal',None,True),functionObj(equalequal)))
defaultVariables.append((strObj('cast',None,True),functionObj(cast)))
defaultVariables.append((strObj('exclamationequal',None,True),functionObj(exclamationequal)))
defaultVariables.append((strObj('exclamationequalequal',None,True),functionObj(exclamationequal)))
defaultVariables.append((strObj('equalequalequal',None,True),functionObj(equalequal)))
defaultVariables.append((strObj('tilde',None,True),functionObj(tilde)))
defaultVariables.append((strObj('backtickperiod',None,True),functionObj(backtickperiod)))
defaultVariables.append((strObj('backtickhashtag',None,True),functionObj(backtickhashtag)))
defaultVariables.append((strObj('exclamation',None,True),functionObj(Not)))
defaultVariables.append((strObj('and',None,True),functionObj(And)))
defaultVariables.append((strObj('pipe',None,True),functionObj(Or)))
defaultVariables.append((strObj('exclamationand',None,True),functionObj(nand)))
defaultVariables.append((strObj('exclamationpipe',None,True),functionObj(nor)))
defaultVariables.append((strObj('greaterequal',None,True),functionObj(greaterequal)))
defaultVariables.append((strObj('lessequal',None,True),functionObj(lessequal)))
defaultVariables.append((strObj('print',None,True),functionObj(Print)))
defaultVariables.append((strObj('println',None,True),functionObj(Println)))
defaultVariables.append((strObj('wait',None,True),functionObj(wait)))
defaultVariables.append((strObj('if',None,True),functionObj(If)))
defaultVariables.append((strObj('while',None,True),functionObj(While)))
defaultVariables.append((strObj('for',None,True),functionObj(For)))
defaultVariables.append((strObj('return',None,True),functionObj(Return)))
defaultVariables.append((strObj('len',None,True),functionObj(Len)))
defaultVariables.append((strObj('input',None,True),functionObj(Input)))
defaultVariables.append((strObj('assert',None,True),functionObj(Assert)))
defaultVariables.append((strObj('true',None,True),booleanObj(True)))
defaultVariables.append((strObj('false',None,True),booleanObj(False)))

for variable in defaultVariables: #hacky way to get the default variables into function objs despite then being made before defaultVariables is done
	for elem in variable:
		if issubclass(type(elem),valueObj):
			elem.__init__(elem.value)
		elif type(elem) is functionObj:
			elem.__init__(elem.func)
for key,stringObj in presetStrObjs.items():
	stringObj.__init__(stringObj.value)
####RUN CODE####
class orange_code:
	def __init__(self):
		self.baseObj=codeObj()
	def setCode(self,code):
		self.baseObj.code=code
	def run(self):
		self.baseObj.run(noneObj())
	def runCode(self,code):
		self.setCode(code)
		self.run()
