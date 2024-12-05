from dfa import DFA
from nfa import NFA as nfa
from reg import RegEx

class InvalidToken(Exception):
	""" 
	Raised if while scanning for a token,
	the lexical analyzer cannot identify 
	a valid token, but there are still
	characters remaining in the input file
	"""
	pass

class Lex:
	def __init__(self, regex_file, source_file):
		"""
		Initializes a lexical analyzer.  regex_file
		contains specifications of the types of tokens, 
		and source_file.
		is the text file that tokens are returned from.
		"""

		self.alphabet = ""
		self.token_list = []
		self.token_num = 0

		# a dic where dic = {TOKEN_TYPE: (regex, reg)}
		self.regex_dic = {}
		
		regex_f = open(regex_file, "r")
		self.source_f = open(source_file, "r")

		# reading the alphabet
		line = regex_f.readline().strip()
		self.alphabet = line[line.find('"') + 1: line.rfind('"')]
 
		# making the regex_dic by reading in regex_f
		for line in regex_f:
			line = line.strip().split()
			expression = line[1][line[1].find('"') + 1: line[1].rfind('"')]

			# intitializing the regex object
			reg = RegEx()
			reg.alphabet = self.alphabet
			reg.expr = expression

			self.regex_dic[line[0]] = (expression, reg)

	def make_token_list(self):
		"""
		Building a list of tokens to iterate through. This is as if each token is separated by space
		"""
		
		# WASgud!!!!!! im treating each token as separated by space first ok.
		for line in self.source_f:
			line = line.strip().split()
			self.token_list += line
	
	def make_better_token_list(self):
		"""
		Building a list of tokens to iterate through. This time not by space.
		"""

		for line in self.source_f:
			line_list = line.strip().split()

			# iterating through each string in a line
			for item in line_list:
				for char in item:
					if char not in self.alphabet:
						self.token_list.append("INVALID")
				start_index = 0
				end_index = 0
				valid_up_to = 0
				valid_type = ""

				# finding a regex within each item
				while start_index < len(item):
					while end_index < len(item):
						if item[end_index] not in self.alphabet:
							break
						
						# testing every regex in the dictionary
						for key in self.regex_dic.keys():
							reg = self.regex_dic[key][1]

							# simulating each regex
							if reg.simulate(item[start_index:end_index+1]):
								valid_type = key
								valid_up_to = end_index
							
								break

						end_index += 1
					
					# if there are no valids
					if valid_type == "":
						if len(self.token_list) != 0:
							if self.token_list[-1] != "INVALID":
								self.token_list.append("INVALID")
						else:
							self.token_list.append("INVALID")
						
						start_index = end_index + 1

					# appending the token and token type to the list
					else:
						self.token_list.append((valid_type, item[start_index:valid_up_to + 1]))
						start_index = valid_up_to + 1
					
					end_index = start_index
					valid_up_to = start_index


	def next_token(self):
		"""
		Returns the next token from the source_file.
		The token is returned as a tuple with 2 item:
		the first item is the name of the token type (a string),
		and the second item is the specific value of the token (also
		as a string).
		Raises EOFError exception if there are not more tokens in the
		file.
		Raises InvalidToken exception if a valid token cannot be identified,
		but there are characters remaining in the source file.
		"""

		# THIS IS WRITING IT AS IF ALL THE TOKENS ARE SEPARATED BY SPACE ALREADY!!!! this passes most cases

		self.make_better_token_list()
		# reading next line in file and returning EOFError if no more tokens
		if self.token_num < len(self.token_list):
			token = self.token_list[self.token_num]
			self.token_num += 1
		else:
			raise EOFError
		
		if token == "INVALID":
			raise InvalidToken
		return token


# You will likely add other classes, drawn from code from your previous 
# assignments.

if __name__ == "__main__":
	num = 1   # can replace this with any number 1, ... 20.
			  # can also create your own test files.
	# reg_ex_filename = f"regex{num}.txt" 
	# source_filename = f"src{num}.txt"
	# lex = Lex(reg_ex_filename, source_filename)
	# try:
	# 	while True:
	# 		token = lex.next_token()
			
	# except EOFError:
	# 	pass
	# except InvalidToken:
	# 	print("Invalid token")

	reg_ex_filename = f"regex9.txt" 
	source_filename = f"src9.txt"
	lex = Lex(reg_ex_filename, source_filename)
	try:
		while True:
			token = lex.next_token()
			
	except EOFError:
		pass
	except InvalidToken:
		print("Invalid token")