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
    #timed_alphabet = None
    timed_alphabet = set()
    states = None
    trans = []
    initstate_name = ""
    accept_names = []
    def __init__(self, automaton=None, flag=None):
        if flag == "generation":
            self.__rta_to_dfa_g(automaton)
        if flag == "receiving":
            self.__rta_to_dfa_r(automaton)
    def __rta_to_dfa_g(self, automaton):
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
        self.timed_alphabet = alphabet_classify(temp_alphabet, automaton.sigma)
    
    def __rta_to_dfa_r(self, automaton):
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
        self.accept_names = automaton.accept_names
        self.timed_alphabet = alphabet_classify(temp_alphabet, automaton.sigma)
    
    def show(self):
        print self.name
        for term in self.timed_alphabet:
            for timedlabel in self.timed_alphabet[term]:
                print timedlabel.get_timedlabel()
        #print self.timed_alphabet.name, self.timed_alphabet.label, self.timed_alphabet.constraint.guard, len(self.timed_alphabet)
        for s in self.states:
            print s.name, s.init, s.accept
        for t in self.trans:
            print t.id, t.source, t.timedlabel.get_timedlabel(), t.target
        print self.initstate_name
        print self.accept_names     

def alphabet_classify(timed_alphabet, sigma):
    temp_set = {}
    for label in sigma:
        temp_set[label] = []
        #label_list = []
        for timed_label in timed_alphabet:
            if timed_label.label == label:
                temp_set[label].append(timed_label)
    return temp_set  

def alphabet_partition(timed_alphabet):
    for key in timed_alphabet:
        timed_labels = timed_alphabet[key]
        for timed_labels
def main():
    A = buildRTA("a.json")
    A.show()
    print("-------------------------------------------")
    A_secret = buildRTA("a_secret.json")
    A_secret.show()
    print("-------------------------------------------")
    B = DFA(A, "generation")
    B.show()
    for timed_label in B.timed_alphabet["a"]:
        print timed_label.get_timedlabel()
    print("-------------------------------------------")
    B_secret = DFA(A_secret, "receiving")
    B_secret.show()
    for timed_label in B_secret.timed_alphabet["b"]:
        print timed_label.get_timedlabel()
    """print rta.name
    for s in rta.states:
        print s.name, s.init, s.accept
    for t in rta.trans:
        print t.id, t.source, t.label, t.target, t.constraint.guard, t.constraint.min_value, t.constraint.closed_min, t.constraint.max_value, t.constraint.closed_max
    print rta.initstate_name
    print rta.accept_names"""

if __name__=='__main__':
	main()          
