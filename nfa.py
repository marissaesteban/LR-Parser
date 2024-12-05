import dfa  # imports your DFA class from pa1

class NFA:
    def __init__(self, filename=None):
        """ Docstring """
        self.numStates = 0
        # Line 2: Alphabet of the language (every character besides the return character is in the language)
        self.alphabet = ""
        # Lines 3 - 3 + Line 1: Transistion fuction of the DFA 
        self.transitions = {}
        # Line after above: Start state of the DFA
        self.startState = []
        # Last line: Accept states of the DFA
        self.acceptStates = []

        if filename !=None:
            file = open(filename)
            
            # reading in first line
            self.numStates = int(file.readline())

            # reading in the alphabet
            self.alphabet = file.readline().strip() + "e"
                
            # reading in state transitions
            line = file.readline()
            while len(line.split()) != 0:
                tmp = line.split()
                from_state = int(tmp[0])
                to_state = int(tmp[2])

                transition_index = self.alphabet.index(tmp[1].strip("'"))

                
                # creating a dictionary of where to transition to per symbol
                if from_state in self.transitions.keys():
                    if self.transitions[from_state][transition_index] == None:
                        self.transitions[from_state][transition_index] = [to_state]
                    else:
                        self.transitions[from_state][transition_index].append(to_state)
                else:
                    self.transitions[from_state] = [None]*len(self.alphabet)
                    self.transitions[from_state][transition_index] = [to_state]
        
                line = file.readline()
                if len(line.split()) == 0:
                    break

            # reading the start state
            self.startState = [int(file.readline())]

            # reading all of the accept states
            line = file.readline()
            tmp = line.split(" ")
            for item in tmp:
                self.acceptStates.append(int(item))
        
        self.alphabet_list = []
        self.make_alphabet_list()

    def make_alphabet_list(self):
        """
        """

        special_chars = "|()*\\N"

        for char in self.alphabet:
            
            if char not in special_chars:
                self.alphabet_list.append(char)
            else:
                self.alphabet_list.append("\\" + char)


    def to_DFA(self):
        """
		Converts the "self" NFA into an equivalent DFA object
		and returns that DFA.  The DFA object should be an
		instance of the DFA class that you defined in pa1. 
		The attributes (instance variables) of the DFA must conform to 
		the requirements laid out in the pa2 problem statement (and that are the same
		as the DFA file requirements specified in the pa1 problem statement).

		This function should not read in the NFA file again.  It should
		create the DFA from the internal representation of the NFA that you 
		created in __init__.
		"""

        epsilonTrans = {}

        # setting up the epsilonTrans dict
        for state in self.transitions.keys():
            if self.transitions[state][len(self.alphabet) - 1] != None:
                epsilonTrans[state] = []
                for item in self.transitions[state][len(self.alphabet) - 1]:
                    if item not in epsilonTrans[state]:
                        epsilonTrans[state].append(item)

        for state in epsilonTrans.keys():
            for item in epsilonTrans[state]:
                if item in epsilonTrans.keys():
                    for s in epsilonTrans[item]:
                        if s not in epsilonTrans[state]:
                            epsilonTrans[state].append(s)

        for state in epsilonTrans.keys():
            if type(epsilonTrans[state]) != int:
                epsilonTrans[state].sort()

        d = dfa.DFA()
        d.alphabet = ""
        for item in self.alphabet:
            if item != "e":
                d.alphabet += str(item)

        # if from the start state, there is epsilon transitions
        for state in self.startState:
            if state in epsilonTrans.keys():
                for item in epsilonTrans[state]:
                    if item not in self.startState:
                        self.startState.append(item)
        
        self.startState.sort()
        new_states = [[0], self.startState]

        q = [self.startState]

        while len(q) > 0:
            #Pop out the state we need to set up transitions for
            curState = q.pop(0)
            
            # if no states in the cur state to transition from
            if curState == []:
                continue
            
            # epsilon transition checker
            #Change
            for state in curState:
                if state in epsilonTrans.keys():
                    for item in epsilonTrans[state]:
                        if item not in curState:
                            curState.append(item)

            curState.sort()

            # make sure that in our DFA transitions dict, we have the curState set up for editing
            if new_states.index(curState) not in d.transitions.keys():
                d.transitions[new_states.index(curState)] = [None] * len(d.alphabet)

            # initialize a list of eventual lists that stores each transition based on alphabet value
            transFunct = [None] * (len(self.alphabet) - 1)
            for state in curState:
                # need to check if we even have transitions for this state
                if state in self.transitions.keys():
                    for i in range(len(self.transitions[state]) - 1):
                        if transFunct[i] == None:
                            transFunct[i] = []
                        if self.transitions[state][i] != None:
                            for item in self.transitions[state][i]:
                                if item not in transFunct[i]:
                                    transFunct[i].append(item)
                                    if item in epsilonTrans.keys():
                                        for s in epsilonTrans[item]:
                                            if s not in transFunct[i]:
                                                transFunct[i].append(s)


            for i in range(len(transFunct)):
                transFunct[i].sort()
                if transFunct[i] not in new_states:
                    new_states.append(transFunct[i])
                    q.append(transFunct[i])
                d.transitions[new_states.index(curState)][i] = new_states.index(transFunct[i])

        d.numStates = len(new_states) - 1
        for i in range(len(new_states)):
            for item in self.acceptStates:
                if item in new_states[i]:
                    d.acceptStates.append(i)
                    break

        if d.numStates > len(d.transitions.keys()):
            reject = 0
            for i in range(1, len(new_states)):
                if new_states[i] == []:
                    reject = i
            for i in range(1, d.num_states + 1):
                if i not in d.transitions.keys():
                    d.transitions[i] = [None] * len(d.alphabet)
                    for j in range(len(d.alphabet)):
                        d.transitions[i][j] = reject

        d.startState = 1

        return d

if __name__ == "__main__":
    nfa = NFA(filename = "nfa7.txt")
    d = nfa.to_DFA()