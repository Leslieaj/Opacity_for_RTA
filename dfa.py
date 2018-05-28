# build a kind of DFA which moves the guards of RTA into the labels

import copy
from rta import *

class TimedLabel:
    name = ""
    label = ""
    constraints = None
    def __init__(self, name="", label="", constraints = None):
        self.name = name
        self.label = label
        self.constraints = constraints or []
    def get_timedlabel(self):
        temp = ""
        for constraint in self.constraints:
            temp = temp + constraint.get_constraint() + 'U'
        constraint_str = temp[:-1]
        return '(' + self.label + ',' + constraint_str + ')'

class DFATran:
    id = None
    source = ""
    target = ""
    label = None
    def __init__(self, id, source="", target="", label=None):
        self.id = id
        self.source = source
        self.target = target
        self.timedlabel = label

class DFA:
    name = ""
    timed_alphabet = None
    states = None
    trans = []
    initstate_name = ""
    accept_names = []
    def __init__(self, automaton=None, flag=None):
        if flag == "generation":
            self.__rta_to_dfa(automaton)
    
    def __rta_to_dfa(self, automaton):
        temp_alphabet = []
        self.trans = []
        for tran in automaton.trans:
            label = copy.deepcopy(tran.label)
            constraint = copy.deepcopy(tran.constraint)
            timed_label = TimedLabel("",label,[constraint])
            temp_alphabet += [timed_label]
            source = tran.source
            target = tran.target
            id = tran.id
            dfa_tran = DFATran(id, source, target, timed_label)
            self.trans.append(dfa_tran)
        self.name = "DFA_" + automaton.name
        self.states = copy.deepcopy(automaton.states)
        self.initstate_name = automaton.initstate_name
        self.accept_names = []
        for state in self.states:
            state.accept = True
            self.accept_names.append(state.name)
        self.timed_alphabet = temp_alphabet
    
    def show(self):
        print self.name
        for term in self.timed_alphabet:
            print term.get_timedlabel()
        #print self.timed_alphabet.name, self.timed_alphabet.label, self.timed_alphabet.constraint.guard, len(self.timed_alphabet)
        for s in self.states:
            print s.name, s.init, s.accept
        for t in self.trans:
            print t.id, t.source, t.timedlabel.get_timedlabel(), t.target
        print self.initstate_name
        print self.accept_names     

def main():
    A = buildRTA("a.json")
    A.show()
    print("-------------------------------------------")
    A_secret = buildRTA("a_secret.json")
    A_secret.show()
    print("-------------------------------------------")
    B = DFA(A, "generation")
    B.show()
    print("-------------------------------------------")
    B_secret = DFA(A_secret, "generation")
    B_secret.show()
    """print rta.name
    for s in rta.states:
        print s.name, s.init, s.accept
    for t in rta.trans:
        print t.id, t.source, t.label, t.target, t.constraint.guard, t.constraint.min_value, t.constraint.closed_min, t.constraint.max_value, t.constraint.closed_max
    print rta.initstate_name
    print rta.accept_names"""

if __name__=='__main__':
	main()          
