from lexer import InvalidToken, Lex

# Exception classes defined for the project.
class NonLRGrammarError(Exception):
    """ Raised when the parser generator detects on non-LR grammar. """

    pass

class SourceFileSyntaxError(Exception):
    """ Raised when the parser determines that the source file does not match the grammar. """

    pass

class Item:
    """ Represents a single item in a state of the LR automaton. 
    
    An item is a single rule from the grammar, plus a dot positioned 
    in the rhs of the rule to indicate how much of the rule has been 
    parsed.
    """
    
    def __init__(self, rule, dot_pos):
        """ Initializes an Item object.

        Parameters:
        rule: Rule
            The rule part of the Item.
        dotpos: int
            Where the dot is in the rule.  (0 if dot is to the left 
            of the leftmost symbol on rhs of rule, 1 if to the right of the
            leftmost symbol on rhs of rule, and so on.)

        Returns None.        
        """

        self.rule = rule
        self.dot_pos = dot_pos

    def __eq__(self, other):
        """ Checks for equality of two items.  """

        if self.__class__ != other.__class__:
            return False
        
        return self.rule == other.rule and self.dot_pos == other.dot_pos
    
    def __hash__(self):
        """ Shows how to hash an Item.  
        
        This then allows an Item to be the key of a dictionary.
        """

        return hash((self.rule, self.dot_pos))
    
class State:
    """ Represents a single state in the LR Automaton. """

    def __init__(self, items):
        """ Initializes a state of the LR Automaton.
        
        Parameters:
        items: set of Item
            The set of items that defines the state.

        Returns None
        """

        self.items = items
        self.action = {} # Dictionary telling what action to take from
        # the "self" state, given the next terminal in the input.  terminal can
        # also be the end of input symbol.  You will fill in this dictionary later.  
        # It should conform to:
        # self.action[terminal] = ("shift", indx)  (shift to state index indx)
        # self.action[terminal] = ("reduce", rule_indx) (reduce by rule whose index is rule_indx)
        # self.action[terminal] = ("accept", ) (accept the input)
        # and if self.action[terminal] is not defined, an error condition - the input is not in the 
        # language of the grammar.
        self.goto = {} # Dictionary telling what state to transition to from this state, 
        # on a reduction operation, given the lhs variable of the rule being reduced.  You
        # will fill in this dictionary later.  It should conform to:
        # self.goto[var] = state_indx (When reducing by a rule for variable var, transition to 
        # # state state_indx)

class Rule:
    """ Represents a single rule of the grammar. """

    def __init__(self, rule, rule_number, lhs, rhs):
        """ Initializes a rule.
        
        Parameters:
        rule: string
            string representation of the rule. For example: "S : A B" (A single space
            separates the different tokens in the rule.)
        rule_number: int
            Rules are numbered so they can be referred to by number in the action and goto 
            dictionaries of a state.
        lhs: string
            Variable on left-hand side of the rule
        rhs: list of strings
            list of symbols that make up the right-hand side of the rule

        Returns None
        """

        self.rule = rule
        self.rule_number = rule_number
        self.lhs = lhs 
        self.rhs = rhs
    
class Parser:
    """ Manages parsing of an input file, given the grammar
        specification, and the specification of the terminals 
        of the grammar.
    """

    def __init__(self, lexer_filename, grammar_filename, source_filename):
        """ Initializes the Parser object.
        
        Parameters:
        lexer_filename: string
            Name of file containing the specifications of the terminals
            of the grammar.  Terminals are specified by regular expressions.
            (Format of this file is specified in pa4 problem statement.)

        grammar_filename: string
            Name of file containing specification of the grammar.  (Format
            of this file is specified in pa5 problem statement.)

        source_filename: string
            Name of the file containing the input to the parser.
        """

        self.end_of_input = "END_OF_INPUT"
        self.dummy_start_symbol = "dummy_start"
        self.start_state_num = 0 # Always 0
        self.epsilon = "eps"  # An epsilon rule in the grammar must have this as its rhs.
        self.accept_action = "accept"

        try:
            # Create lexical analyzer.  Use code from pa4 for this.
            self.lexer = Lex(lexer_filename, source_filename)

            # Read the grammar file.
            self.terminals, self.nonterminals, self.rules, self.rules_by_lhs = \
                self.read_grammar_file(grammar_filename)

            # Compute first and follow functions for the input grammar.
            self.first = self.compute_first()
            self.follow = self.compute_follow()

            # Compute the parse table for the grammar.
            self.states = self.compute_parse_table_states()
        
        except InvalidToken:
            print(f"Invalid token while processing input file {source_filename}")

    def read_grammar_file(self, grammar_filename):
        """ Reads the grammar file, initializing instance variables associated with the grammar.
        
        Parameters:

        grammar_filename: string
            Name of file containing grammar specification.

        Returns: (terminals, nonterminals, rules, rules_by_lhs):

        terminals: set
            Set of grammar terminals

        nonterminals: set
            Set of grammar nonterminals (variables)

        rules: list of Rule
            List of grammar rules

        rules_by_lhs: dict
            Dictionary mapping grammar nonterminals to set of rules
            for that nonterminal.

        Exceptions raised:

        FileNotFoundError, if grammar file could not be opened.

        Returns None.
        """
        try:
            # Open file                                                                                                           fd
            f = open(grammar_filename)

            # Initialize variables to store grammar.
            terminals = set()
            nonterminals = set()
            rules = []  
            rules_by_lhs = {}

            # Start counting the rules
            rule_number = 0

            # Read terminals
            while True:
                line = f.readline()
                if line.strip() == "%%":
                    break
                line_terminals = line.split()
                for term in line_terminals:
                    terminals.add(term)
            
            # Add end of input terminal
            terminals.add(self.end_of_input)

            # Read first rule from file.
            line = f.readline()
            rule = self.parse_rule(line, 1)  # Will be rule number 1

            # Create dummy first rule
            nonterminals.add(self.dummy_start_symbol)
            self.dummy_rule = Rule("", rule_number, self.dummy_start_symbol, (rule.lhs,))
            rules.append(self.dummy_rule)
            rules_by_lhs[self.dummy_start_symbol] = {self.dummy_rule}

            # Add first rule from file
            rule_number += 1
            nonterminals.add(rule.lhs)
            rules.append(rule)
            rules_by_lhs[rule.lhs] = {rule}

            # Read remaining rules
            while True:
                # Get the line
                line = f.readline()

                # Check for end of file
                if len(line.strip()) == 0:
                    break
           
                # Check for end of section
                if line.strip() == "%%":
                    break

                # Got another rule
                rule_number += 1
                
                # Process
                rule = self.parse_rule(line, rule_number)
                nonterminals.add(rule.lhs)
                rules.append(rule)
                if rule.lhs not in rules_by_lhs:
                    rules_by_lhs[rule.lhs] = {rule}
                else:
                    rules_by_lhs[rule.lhs].add(rule)
            
            # Return data
            return terminals, nonterminals, rules, rules_by_lhs
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not open grammar file {grammar_filename}")
        
    def parse_rule(self, line, rule_number):
        """ Parse a single rule from the grammar 
        
        Parameters:

        line: string
            Line containing the rule
        
        rule_number: int
            Number assigned to this rule

        Returns: Rule
            The rule that was read in.
        """

        # Strip leading and trailing spaces
        temp_line = line.strip()

        # Get the rule
        tokens = tuple(temp_line.split())
        rule = " ".join(tokens)

        return Rule(rule, rule_number, tokens[0], tokens[2:])

    def compute_first(self):
        """
        Compute first dictionary for all grammar symbols, and for
        all strings of grammar symbols that follow a nonterminal
        in a rule.
        Assumes epsilon only appears in a rule of the form X -> epsilon.

        Returns: dict
            key is string that is any terminal, nonterminal, or any 
            substring of a rule rhs following a nonterminal in the rule rhs.
            value is the set of terminals that can appear first in a string
            derived from the nonterminal.
        """
        # Initialize
        first = {}
        for nonterminal in self.nonterminals:
            first[nonterminal] = set()
        for terminal in self.terminals:
            first[terminal] = {terminal}

        # Compute first for all nonterminals
        
        # Handle rules of the form X -> epsilon
        for rule in self.rules:
            if rule.rhs[0] == self.epsilon:
                first[rule.lhs].add(self.epsilon)

        # Handle other rules.  Keep going until all rules
        # are processed without adding anything to first for a nonterminal.
        while True:
            updated = False
            # Check every rule
            for rule in self.rules:
                # Skip epsilon rules
                if rule.rhs[0] == self.epsilon:
                    continue

                first_of_rhs = self.first_of_substring(first, rule.rhs)
                if not first_of_rhs.issubset(first[rule.lhs]):
                    updated = True
                    first[rule.lhs].update(first_of_rhs)
      
            if not updated:
                # All done
                break
                
        # Compute first for all strings of grammar symbols that follow a nonterminal
        # in a rule
        for rule in self.rules:
            for i in range(len(rule.rhs) - 1):
                if rule.rhs[i] in self.nonterminals:
                    str = rule.rhs[i+1:]
                    first[str] = self.first_of_substring(first, str)

        # Return first
        return first

    def first_of_substring(self, first, symbols):
        """
        Returns the first function of the list of symbols.

        Parameters

        first: dict
            First dictionary where key is a grammar symbol,
            and value is the set of terminals that can appear
            first in a string derived from the grammar symbol.

        symbols: string
            List of symbols whose first function is to be
            computed.

        Returns: set
            Returns set that is the first function of symbols.
        """

        # Initialize first set to return
        first_to_return = set()

        # Check symbols from left to right
        all_symbols_generate_eps = True
        for symbol in symbols:
            terminals = first[symbol]
            for terminal in terminals:
                if terminal != self.epsilon:
                    first_to_return.add(terminal)
            if self.epsilon not in first[symbol]:
                # Don't check any more symbols in rhs of this rule
                all_symbols_generate_eps = False
                break 

        if all_symbols_generate_eps:
            first_to_return.add(self.epsilon)

        return first_to_return
                
    def compute_follow(self):
        """ Compute and return follow dictionary for all nonterminals in the grammar.

        Returns: dict
            key is nonterminal in the grammar.
            value is the set of terminal symbols that can follow 
            a string derived by the nonterminal.
        """

        # Initialize
        follow = {}
        for nonterminal in self.nonterminals:
            follow[nonterminal] = set()
        follow[self.dummy_start_symbol].add(self.end_of_input)

        # Compute follow for all nonterminals

        # Keep adding terminals to follow until no more can be added
        while True:
            updated = False
            for rule in self.rules:
                for i in range(len(rule.rhs) - 1):
                    symbol = rule.rhs[i]
                    if symbol in self.nonterminals:
                        remainder = rule.rhs[i+1:]
                        first_remainder = self.first[remainder]
                        for terminal in first_remainder:
                            if terminal != self.epsilon and terminal not in follow[symbol]:
                                follow[symbol].add(terminal)
                                updated = True
                        if self.epsilon in first_remainder:
                            for terminal in follow[rule.lhs]:
                                if terminal not in follow[symbol]:
                                    follow[symbol].add(terminal)
                                    updated = True

                # Handle last symbol on rhs
                symbol = rule.rhs[-1]
                if symbol in self.nonterminals:
                    for terminal in follow[rule.lhs]:
                        if terminal not in follow[symbol]:
                            follow[symbol].add(terminal)
                            updated = True

            if not updated:
                # all done
                break

        # All done. Return follow dictionary
        return follow
    
    def compute_parse_table_states(self):
        """ Compute the states of the parse table 

        Returns: set of State
            Returns set of states of the parse tables.
        """
        # Initialize set of states with start state
        start_items = {Item(self.rules[0], 0)}
        start_state = State(self.items_closure(start_items))
        states = [start_state]

        i = 0
        while i < len(states):

            #Get the state we need to generate the action and goto for
            state = states[i]

            #Checking to see if we need to add the end of input transition to the action
            for item in list(state.items):
                if item.rule.rule_number == 0 and item.dot_pos == 1:
                    if self.end_of_input in state.action.keys():
                        raise NonLRGrammarError
                    state.action[self.end_of_input] = (self.accept_action,)

            #Creating our pre process dict for every item to the right of the dot on the rhs
            pre_process_dict = {}
            for item in state.items:
                rule = item.rule
                #No point in doing anything if the dot pos is at the end
                if item.dot_pos < len(rule.rhs):
                    if rule.rhs[item.dot_pos] in pre_process_dict.keys():
                        pre_process_dict[rule.rhs[item.dot_pos]].append(item)
                    else:
                        pre_process_dict[rule.rhs[item.dot_pos]] = [item]

                if item.dot_pos == len(rule.rhs):
                    lst = self.follow[rule.lhs]
                    for key in lst:
                        if key != "eps":
                            if key not in state.action.keys():
                                state.action[key] = ("reduce", item.rule.rule_number)
                            else:
                                temp = state.action[key]
                                if temp[0] != self.accept_action:
                                    raise NonLRGrammarError

            for key in pre_process_dict.keys():
                #Checks to see if we already have a transition for key in action or goto
                if key in state.action.keys() or key in state.goto.keys():
                    raise NonLRGrammarError

                lst = pre_process_dict[key]
                new_items = set()

                # Move the dot position by one to the right
                for item in lst:
                    temp = Item(item.rule, item.dot_pos + 1)
                    new_items.add(temp)

                # Generate the set of closed items
                new_items = self.items_closure(new_items)

                # State already exists
                if self.get_state_index(new_items, states) != None:
                    shift_ind = self.get_state_index(new_items, states)
                    if key in self.terminals:
                        state.action[key] = ("shift", shift_ind)
                    elif key != "eps" and key != self.end_of_input:
                        state.goto[key] = shift_ind
                # Need to create a new state
                else:
                    new_state = State(new_items)
                    states.append(new_state)
                    if key in self.terminals:
                        state.action[key] = ("shift", len(states) - 1)
                    elif key != "eps" and key != self.end_of_input:
                        state.goto[key] = len(states) - 1
            i += 1
        return states
        
    def goto(self, state, symbol):
        """ Gets the set of items to transition to from a state in the LR automaton.

        Parameters:

        state: int
            The state being transitioned from.

        symbol: string
            The grammar symbol (terminal or nonterminal) being transitioned on.

        Returns: set of Item
            The set of items that will define the state to transition to. 
        """

        goto_items = set()
        for item in state.items:
            if item.dot_pos < len(item.rule.rhs) and symbol == item.rule.rhs[item.dot_pos]:
                goto_items.add(Item(item.rule, item.dot_pos + 1))
        goto_items = self.items_closure(goto_items)
        return goto_items
    
    def get_state_index(self, items, states):
        """ Get index of state that contains the specified items.
        
        Parameters:

        items: set of Item
            The set of items to search for in the state list.

        states: list of State
            the list of states to search for the set of items.

        Returns: int or None
            Returns the index of the state belonging to the set of Items,
            or None if the set of items not found in the list of state.
        """

        for i, state in enumerate(states):
            if items == state.items:
                return i
        return None

    def items_closure(self, items):
        """ Updates set of items to contain the closure of itself.

        Parameters:

        items: set of Item
            The set of items to compute the closure of.

        Returns: set of Item
            Returns the closure of the set of items.
        """

        # Keep adding new items until no more items are added.
        while True:
            new_items = set()
            for item in items:
                rule = item.rule
                rhs = rule.rhs
                dot_pos = item.dot_pos
                if dot_pos < len(rhs) and rhs[dot_pos] in self.nonterminals:
                    nonterminal = rhs[dot_pos]
                    for rule in self.rules_by_lhs[nonterminal]:
                        item = Item(rule, 0)
                        if item not in items:
                            new_items.add(item)
            if not new_items:
                break
            else:
                items.update(new_items)
        return items
    
    def parse(self):
        """ Parse the source file.

        Returns: list
            Returns the parse tree for the source file, returned as a list generated
            by visiting the nodes of the parse tree in depth-first, pre-order fashion.
            Each node of the parse tree is a string containing a grammar symbol - nonterminals for 
            interior nodes, and terminals (or eps) for leaf nodes.

        Exceptions raised:

        lex.InvalidToken: raised by the next_token method of the Lex class
        if the next symbols in the input are not a valid token.

        NonLRGrammarError: raised by the parse method of the Parser class
        if the method detects that the input grammar is no an LR(1) grammar.

        SourceFileSyntaxError: raised by the parse method of the Parser class
        if the method detects that the next input token is valid for the grammar.
        """
        
        #Create states
        states = self.compute_parse_table_states()

        #Initialize stack
        stack = [(states[0], None)]

        next_input = self.lexer.next_token()
        while True:
            if next_input[0] not in stack[-1][0].action.keys():
                #Flag is to break out of loop, if we dont have an epsilon transition within the state that has no actions for the next input
                flag = 1
                for item in stack[-1][0].items:
                    if item.rule.rhs[0] == "eps":
                        flag = 0
                        temp = Node("eps")
                        node = Node(item.rule.lhs)
                        node.children.append(temp)
                        stack.append((states[stack[-1][0].goto[item.rule.lhs]], node)) 
                        break
                if flag == 1:
                    raise SourceFileSyntaxError

            else:
                action = stack[-1][0].action[next_input[0]]

                if action[0] == "shift":
                    #Create a new node for the shifted state and add it to stack
                    node = Node(next_input[1])
                    stack.append((states[action[1]], node))
                    try:
                        next_input = self.lexer.next_token()
                    except EOFError:
                        next_input = ('END_OF_INPUT', 'end')

                elif action[0] == "reduce":
                    rule = self.rules[action[1]]

                    # pop len(rhs) of the rule states off the stack and add them to the children of the new node
                    node = Node(rule.lhs)
                    for _ in range(len(rule.rhs)):
                        node.children.append(stack.pop())

                    # goto the correct state based on goto dict and add node to stack
                    where_to_go = stack[-1][0].goto[rule.lhs]
                    stack.append((states[where_to_go], node))
            
                elif action[0] == self.accept_action:
                    #Accepts!
                    break
                    
        root = stack.pop()
        ret = []
        
        #Preorder traversal code
        def preorder_trav(root):
            if not root:
                return

            if type(root) == Node:
                ret.append(root.item)
                for child in reversed(root.children):
                    preorder_trav(child)
            else:
                ret.append(root[1].item)

                for child in reversed(root[1].children):
                    preorder_trav(child)

        preorder_trav(root)
        return ret

class Node:
    """ 
    Node class to hold state and item for parsing as well as children for tree
    """
    def __init__(self, item):
        self.item = item
        self.children = []

if __name__ == "__main__":
    lexer_filename = "tokens1.txt"
    grammar_filename = "grammar1.txt"
    source_filename = "src1.txt"
    correct_filename = "correct1.txt"

    parser = Parser(lexer_filename, grammar_filename, source_filename)
    
    # Read first line of correct file.
    correct_results_file = open(correct_filename)
    correct_answer = correct_results_file.readline().strip()

    try:
        # Create parser, and parse
        parser = Parser(lexer_filename, grammar_filename, source_filename)
        parse_tree = parser.parse()

        if correct_answer == "InvalidToken":
            print("Incorrect.  You should have raised InvalidToken exception (in source file)")
        elif correct_answer == "NonLRGrammarError":
            print("Incorrect.  You should have raised NonLRGrammar exception")
        elif correct_answer == "SourceFileSyntaxError":
            print("Incorrect.  You should have raised SourceFileSyntaxError exception")
        else:
            # Make sure parse returns correct parse tree

            # Read correct parse tree
            correct_parse_tree = [node for node in correct_results_file.readline().split()]
            if parse_tree == correct_parse_tree:
                print("Correct.  Parse tree correct")
            else:
                print("Incorrect.")
                print(f"Your parse tree = {parse_tree}")
                print(f"Correct parse tree = {correct_parse_tree}")

    except InvalidToken:
        if correct_answer == "InvalidToken":
            print("Invalid token in source file.  Correct")
        else:
            print("Incorrect.  You raise invalid token when there is not one")
    except NonLRGrammarError:
        if correct_answer == "NonLRGrammarError":
            print("NonLRGrammarError.  Correct")
        else:
            print("Incorrect.  You raise NonLRGrammarError when there is not one")
    except SourceFileSyntaxError:
        if correct_answer == "SourceFileSyntaxError":
            print("SourceFileSyntaxError.  Correct")
        else:
            print("Incorrect.  You raise SourceFileSyntaxError when there is not one")
