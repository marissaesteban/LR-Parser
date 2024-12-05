import sys

class FileFormatError(Exception):
    """
    Exception that is raised if the 
    input file to the DFA constructor
    is incorrectly formatted.
    """

    pass

class DFA:
    def __init__(self, *, filename=None):
        """
        Initializes DFA object from the dfa specification
        in named parameter filename.
        """
        # DFA file format:
        # Line 1: Number of States
        self.numStates = 0
        # Line 2: Alphabet of the language (every character besides the return character is in the language)
        self.alphabet = ""
        # Lines 3 - 3 + Line 1: Transistion fuction of the DFA (We can discuss how to actually store this in the best way)
        self.transitions = {}
        # Line after above: Start state of the DFA
        self.startState = 0
        # Last line: Accept states of the DFA
        self.acceptStates = []
 
        if filename != None:
            file = open(filename)

            try: 

                # reading in first line
                self.numStates = int(file.readline())

                # reading in the alphabet
                self.alphabet = file.readline() 
                
                # reading in state transitions
                for i in range(self.numStates * (len(self.alphabet)-1)):
                    line = file.readline()
                    tmp = line.split()
                    from_state = int(tmp[0])
                    to_state = int(tmp[2])
                    
                    # making sure only valid states
                    if from_state < 1 or from_state > self.numStates:
                        raise FileFormatError
                    elif to_state < 1 or to_state > self.numStates:
                        raise FileFormatError

                    transition_index = self.alphabet.index(tmp[1].strip("'"))                

                    # creating a dictionary of where to transition to per symbol
                    if from_state in self.transitions.keys():
                        self.transitions[from_state][transition_index] = to_state
                    else:
                        self.transitions[from_state] = [None]*len(self.alphabet)
                        self.transitions[from_state][transition_index] = to_state

                # start state
                self.startState = int(file.readline())
                if self.startState < 1 or self.startState > self.numStates:
                            raise FileFormatError

                final_line = file.readline().split()
                if len(final_line) == 0:
                    self.acceptStates = None
                else:
                    self.acceptStates = [int(item) for item in final_line]

                # making sure its the end of the file
                if len(file.readline()) != 0:
                    raise FileFormatError

            
            except TypeError and ValueError: # something about when a file has nothing left to read?
                raise FileFormatError
            
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

    @property
    def num_states(self):
        """ Number of states property """
        return self.numStates

    @num_states.setter
    def num_states(self, val):
        self.numStates = val

    @property
    def start_state(self):
        return self.startState

    @start_state.setter
    def start_state(self, val):
        self.startState = val

    @property
    def accept_states(self):
        return self.acceptStates

    @accept_states.setter
    def accept_states(self, l):
        self.acceptStates = l

    def transition(self, state, symbol):
        """
        Returns the state to transition to from "state" on in input symbol "symbol".
        state must be in the range 1, ..., num_states
        symbol must be in the alphabet
        the returned state must be in the range 1, ..., num_states
        """

        # what state should we transition to
        index = self.alphabet.index(symbol)
        transition_states = self.transitions[state]

        return transition_states[index]
        
        # making sure the state exists
        if (curState == None):
            raise FileFormatError
        elif curState not in self.transitions.keys():
            raise FileFormatError
        
    def simulate(self, test_string):
        """
        Returns True if str is in the language of the DFA,
        and False if not.

        Assumes that all characters in str are in the alphabet 
        of the DFA.
        """

        # if there aren't any accept states
        if self.acceptStates == None:
            return False

        curState = self.startState

        try:

            # iterating through the string
            for letter in test_string:

                # what state should we transition to
                index = self.alphabet.index(letter)
                transition_states = self.transitions[curState]

                curState = transition_states[index]
                
                # making sure the state exists
                if (curState == None):
                    raise FileFormatError
                elif curState not in self.transitions.keys():
                    raise FileFormatError

        except ValueError:
            raise FileFormatError

        if curState in self.acceptStates:
            return True
        return False

if __name__ == "__main__":
    # You can run your dfa.py code directly from a
    # terminal command line:

    # Check for correct number of command line arguments

    # if len(sys.argv) != 3:
    #     print("Usage: python3 pa1.py dfa_filename str")
    #     sys.exit(0)

    # dfa = DFA(filename = sys.argv[1])
    # str = sys.argv[2]
    # ans = dfa.simulate(str)
    # if ans:
    #     print(f"The string {str} is in the language of the DFA")
    # else:
    #     print(f"The string {str} is in the language of the DFA")

    dfa = DFA(filename = "dfa19.txt")
    f = open("dfa19.txt")
    strs = []
    for line in f:
        strs.append(line.strip())
    for item in strs:
        ans = dfa.simulate(item)
        print(item)
        print(ans)