from dfa import DFA
from nfa import NFA as nfa
class InvalidExpression(Exception):    
	pass

class LeafNode():
	def __init__(self, symbol):
		self.symbol = symbol

	def to_nfa(self, alphabet):
		"""
		Defining the nfa for a terminal symbol
		"""

		self.nfa = nfa()
		self.nfa.numStates = 2
		self.nfa.alphabet = alphabet

		# defining the transition dictionary
		for i in range(self.nfa.numStates):
			self.nfa.transitions[i + 1] = [None]*(len(self.nfa.alphabet) - 1)
			self.nfa.transitions[i + 1].append([])

		# defining the transition from state 1 to 2
		if self.symbol[0] == "\\":
			symbol = self.symbol[1]
			index = self.nfa.alphabet.index(symbol)
		else:
			index = self.nfa.alphabet.index(self.symbol)

		self.nfa.transitions[1][index] = [2]
		self.nfa.startState = [1]
		self.nfa.acceptStates = [2]

		return self.nfa
	
	def __str__(self):
		return ("I'm a terminal node with the symbol: " + self.symbol)

class EmptyNode():
	def __init__(self, symbol):
		self.symbol = symbol

	def to_nfa(self, alphabet):

		self.nfa = nfa()
		self.nfa.numStates = 2
		self.nfa.alphabet = alphabet

		# defining the transition dictionary
		for i in range(self.nfa.numStates):
			self.nfa.transitions[i + 1] = [None]*(len(self.nfa.alphabet))

		for i in range(len(self.nfa.transitions[1])):
			for j in range(len(alphabet)):
				self.nfa.transitions[1][j] = [2]

		self.nfa.startState = [1]
		self.nfa.acceptStates = [1]

		return self.nfa

class StarNode():

	def __init__(self, symbol):
		self.symbol = symbol
		self.left = ""

	def __str__(self):
		return ("I'm a terminal node with the symbol: "+ self.symbol)

	def to_nfa(self, stack):
		temp = stack.pop()

		self.nfa = nfa()
		self.nfa.numStates = temp.numStates
		self.nfa.alphabet = temp.alphabet
		self.nfa.transitions = temp.transitions
		self.nfa.startState = temp.startState
		self.nfa.acceptStates = temp.acceptStates

		# making epsilon transitions from the accept state to the start state
		for item in temp.acceptStates:
			if item in self.nfa.transitions.keys():
				if self.nfa.transitions[item][-1] != [None]:
					self.nfa.transitions[item][-1].append(self.nfa.startState[0])
				else:
					self.nfa.transitions[item][-1] = [self.nfa.startState[0]]

			else:
				self.nfa.transitions[item] = [None]*len(self.alphabet - 1)
				self.nfa.transitions[item].append([])
				self.nfa.transitions[item][-1].append(temp.startState[0])

		# making the start state an accept state
		if self.nfa.startState[0] not in self.nfa.acceptStates:
			self.nfa.acceptStates.append(self.nfa.startState[0])
		return self.nfa

class UnionNode():
	def __init__(self, symbol):
		self.symbol = symbol
		self.left = ""
		self.right = ""
	
	def __str__(self):
		return ("I'm a Union node with the symbol: " + self.symbol)

	def to_nfa(self, stack):
		
		top = stack.pop() # left side of union
		bottom = stack.pop() # right side of concat

		self.nfa = nfa()
		self.nfa.numStates = top.numStates + bottom.numStates + 1
		self.nfa.alphabet = top.alphabet
		
		# defining the transition dictionary
		new_dic = {}
		for key in bottom.transitions.keys():
			new_val = bottom.transitions[key]
			for i in range(len(new_val)):
				if new_val[i] != None:
					for j in range(len(new_val[i])):
						if new_val[i][j] != None:
							new_val[i][j] += 1
			new_dic[key+1] = new_val

		# shifting the state numbers for the second nfa
		for key in top.transitions.keys():
			new_val = top.transitions[key]
			for i in range(len(new_val)):
				if new_val[i] != None:
					for j in range(len(new_val[i])):
						if new_val[i][j] != None:
							new_val[i][j] += (1 + bottom.numStates)

			new_dic[key + (1 + bottom.numStates)] = new_val

		self.nfa.transitions = new_dic

		# defining the epsilon transition
		if 1 in self.nfa.transitions:
			self.nfa.transitions[1][-1] = [2, 2 + bottom.numStates]
		else:
			self.nfa.transitions[1] = [None]*len(self.nfa.alphabet)
			self.nfa.transitions[1][-1] = [2, 2 + bottom.numStates]

		self.nfa.startState = [1]

		a1 = [x + 1 if x is not None else x for x in bottom.acceptStates]
		a2 = [x + (1 + bottom.numStates) if x is not None else x for x in top.acceptStates]
		self.nfa.acceptStates = a1 + a2

		return self.nfa


class ConcatNode():

	def __init__(self, symbol):
		self.symbol = symbol
		self.left = ""
		self.right = ""

	def __str__(self):
		return ("I'm a terminal node with the symbol: " + self.symbol)

	def to_nfa(self, stack):
		
		top = stack.pop() # right side of concat
		bottom = stack.pop() # left side of concat

		self.nfa = nfa()
		self.nfa.startState = [1]
		self.nfa.numStates = top.numStates + bottom.numStates
		self.nfa.alphabet = top.alphabet
		self.nfa.transitions = bottom.transitions

		# adding in the epsilon transition
		for accept_state in bottom.acceptStates:
			self.nfa.transitions[accept_state][-1].append(top.startState[0] + bottom.numStates)
		
		# combining the transition dictionaries
		for key in top.transitions.keys():
			new_key = key + bottom.numStates
			new_val = top.transitions[key]

			for item in new_val:
				if item != None:
					for i in range(len(item)):
						item[i] += bottom.numStates

			self.nfa.transitions[new_key] = new_val

		self.nfa.acceptStates = []
		for item in top.acceptStates:
			self.nfa.acceptStates.append(item + bottom.numStates)

		return self.nfa

class RegEx:

	def __init__(self, filename):
		"""
		Initializes regular expression from the file "filename"
		"""
		self.alphabet = ""
		self.alphabet_list = []
		self.expr = ""

		file = open(filename)

		line = file.readline().strip()
		self.alphabet = line[line.find('"') + 1: line.rfind('"')]
 

		line = file.readline().strip()
		self.expr = line[line.find('"') + 1: line.rfind('"')]
	
	def make_alphabet_list(self):
		"""
		Creates an alphabet list, to handle special characters in add_concats
		"""

		special_chars = "|()*\\N"

		# defining a list for every character in the alphabet including "\\"
		for char in self.alphabet:
			
			if char not in special_chars:
				self.alphabet_list.append(char)
			else:
				self.alphabet_list.append("\\" + char)

	def add_concats(self):
		"""
		Adds the & character to represent a concat operation
		"""

		self.make_alphabet_list()

		previous = self.expr[0]
		new_str = previous

		skip = -1
		for i in range(1, len(self.expr)):


			if i != skip:
				
				# if the character is a "\" then skip the next character
				if self.expr[i] == "\\":
					item = self.expr[i:i+2]
					skip = i+1
				else:
					item = self.expr[i]

				# A( or AA
				if previous in self.alphabet_list and (item == "(" or item in self.alphabet_list):
					new_str += "&"

				# *( or *A
				elif previous == "*" and (item == "(" or item in self.alphabet_list):
					new_str += "&"

				# )( or )A
				elif previous == ")" and (item == "(" or item in self.alphabet_list):
					new_str += "&"
				
				new_str += item
				previous = item

		self.expr = new_str

	def to_syntax_tree(self):
		"""
		Returns an syntax tree object that is equivalent to 
		the "self" regular expression
		"""

		# defining the precedence for operators
		precedence_dict = {"*": 2, "&": 1, "|": 0, "(": -1}

		#Contains references to nodes of syntax tree (i.e. characters in the alphabet)
		operandStack = []

		#Contains operators of the syntax tree (including the left parentesis "(" )
		operatorStack = []

		self.add_concats()
		skip = -1

		# going through each character in the expr to make nodes to push onto stacks
		for i in range(len(self.expr)):

			if i != skip:
				item = self.expr[i]

				# skip the next item if the character is a "\"
				if item == "\\":
					item = item + self.expr[i+1]
					skip = i + 1
				
				if item in self.alphabet_list and item != "*" and item != "|" and item != "&":
					n = LeafNode(item)
					operandStack.append(n)
	
				elif item in self.alphabet_list:
					n = LeafNode(item)
					operandStack.append(n)

				elif item == "e":
					n = EmptyNode(item)
					operandStack.append(n)

				elif item == "(":
					operatorStack.append(item)

				elif item == ")":
					
					op = operatorStack.pop()

					# pop operators until left paren is popped off
					while op != "(":

						if op == "*":
							n = StarNode(op) # FIX ME
							left = operandStack.pop()
							n.left = left # FIX ME 
							operandStack.append(n)

						elif op == "&":
							n = ConcatNode(op) # FIX ME
							right = operandStack.pop()
							left = operandStack.pop()
							n.right = right
							n.left = left
							operandStack.append(n)

						else:
							n = UnionNode(op) # FIX ME
							right = operandStack.pop()
							left = operandStack.pop()
							n.right = right
							n.left = left
							operandStack.append(n)

						op = operatorStack.pop()
				
				# if it's an operator (star, union or concact)
				else:

					# while the op stack isnt empty, and top of stack is op thats >= item scanned
					while len(operatorStack) != 0 and (precedence_dict[operatorStack[-1]] >= precedence_dict[item]):
						op = operatorStack.pop()

						if op == "*":
							n = StarNode(op)
							left = operandStack.pop()
							n.left = left
							operandStack.append(n)

						elif op == "&":
							n = ConcatNode(op)
							right = operandStack.pop()
							left = operandStack.pop()
							n.right = right
							n.left = left
							operandStack.append(n)

						else:
							n = UnionNode(op)
							right = operandStack.pop()
							left = operandStack.pop()
							n.right = right
							n.left = left
							operandStack.append(n)

					operatorStack.append(item)


		# empty the operator stack and create node from it
		while len(operatorStack) != 0:
			op = operatorStack.pop()

			if op == "*":
				n = StarNode(op)
				left = operandStack.pop()
				n.left = left
				operandStack.append(n)
			elif op == "&":
				n = ConcatNode(op)
				right = operandStack.pop()
				left = operandStack.pop()
				n.right = right
				n.left = left
				operandStack.append(n)
			else:
				n = UnionNode(op)
				right = operandStack.pop()
				left = operandStack.pop()
				n.right = right
				n.left = left
				operandStack.append(n)
		
		syntax_tree = operandStack.pop()
		return syntax_tree

	def to_nfa(self):
		"""
		Returns an NFA object that is equivalent to 
		the "self" regular expression
		"""
		syntax_tree = self.to_syntax_tree()
		self.stack = []

		#Post order traversal of the syntax tree
		def postOrder(root):
			if root:
				try:
					postOrder(root.left)
				except Exception:
					pass

				try:
					postOrder(root.right)
				except Exception:
					pass

				#Converts the item in syntax tree to a nfa
				#For leaf node
				if root.symbol in self.alphabet_list or root.symbol == "e":
					temp = root.to_nfa(self.alphabet + "e")
					self.stack.append(temp)
				#For interior
				else:
					temp = root.to_nfa(self.stack)
					self.stack.append(temp)

		postOrder(syntax_tree)

		return self.stack.pop()

	def simulate(self, str):
		"""
		Returns True if str is in the languages defined
		by the "self" regular expression
		"""

		#Handles the "e" regex on 3 and 20
		if self.expr != "e":
			nfa = self.to_nfa()
		else:
			if str != '':
				return False
			else:
				return True

		# Converts nfa to dfa
		dfa = nfa.to_DFA()

		return dfa.simulate(str)

if __name__ == "__main__":
	# for debuggin
	filename = "emptyString.txt"
	re = RegEx(filename)

	test_file = "test.txt"
	test_file = open(test_file, "r")
	for line in test_file:
		line = line.strip()
		test_str = line[line.find('"') + 1: line.rfind('"')]

		valid = re.simulate(test_str)
