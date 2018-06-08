#projection

from rta import *
from dfa import *


class BTau:
    def __init__(self, states, timed_alphabet, trans, initstates, accept):
        self.states = states or []
        self.timed_alphabet = timed_alphabet or []
        self.trans = trans or []
        self.initstate_name = initstates
        self.accept_names = accept or []
    def show(self):
        #print self.name
        for timedlabel in self.timed_alphabet:
            print timedlabel.get_timedlabel()
        #print self.timed_alphabet.name, self.timed_alphabet.label, self.timed_alphabet.constraint.guard, len(self.timed_alphabet)
        for s in self.states:
            print s.name, s.init, s.accept
        for t in self.trans:
            print t.id, t.source, t.timedlabel.get_timedlabel(), t.target
        print self.initstate_name
        print self.accept_names 

def isinBTAlphabet(timedlabel, timed_alphabet):
    for temp in timed_alphabet:
        if timedlabel.get_timedlabel() == temp.get_timedlabel():
            return True
    return False

def buildBTau(dfa, observable):
    states = copy.deepcopy(dfa.states)
    trans = []
    temp_alphabet = []
    initstate_name = [dfa.initstate_name]
    accept_names = copy.deepcopy(dfa.accept_names)
    #accept_names = []
    for tran in dfa.trans:
        if tran.timedlabel.label not in observable:
            index = len(trans)
            new_timedlabel = TimedLabel("Tau"+str(len(temp_alphabet)), "Tau", tran.timedlabel.constraints)
            new_tran = DFATran(index, tran.source, tran.target, new_timedlabel)
            trans.append(new_tran)
            if isinBTAlphabet(tran.timedlabel, temp_alphabet) == False:
                temp_alphabet.append(new_timedlabel)
        else:
            if tran.target not in initstate_name:
                initstate_name.append(tran.target)
            if tran.source not in accept_names:
                accept_names.append(tran.source)
    for s in states:
        s.init = False
        s.accept = False
        if s.name in initstate_name:
            s.init = True
        if s.name in accept_names:
            s.accept = True
    return BTau(states, temp_alphabet, trans, initstate_name, accept_names)

def main():
    A = buildRTA("a.json")
    A.show()
    print("-------------------------------------------")
    A_secret = buildRTA("a_secret.json")
    A_secret.show()
    print("-------------------------------------------")
    B = DFA(A, "generation")
    B.show()
    #for timed_label in B.timed_alphabet["a"]:
    #    print timed_label.get_timedlabel()
    print("-------------------------------------------")
    B_secret = DFA(A_secret, "receiving")
    B_secret.show()
    #for timed_label in B_secret.timed_alphabet["b"]:
    #    print timed_label.get_timedlabel()
    print("---------------------------------------------")
    pa1,l1 = alphabet_partition(B.timed_alphabet)
    pa2,l2 = alphabet_partition(B_secret.timed_alphabet)
    pa3,l3 = alphabet_partition(alphabet_combine(B.timed_alphabet, pa2))
    for term in pa3:
        for timedlabel in pa3[term]:
            print timedlabel.name, timedlabel.get_timedlabel()
    for term in l3:
        for bn,index in zip(l3[term],range(len(l3[term]))):
            print index, bn.getbn()
    print("--------------------------------------------")
    B_refined = RefinedDFA(B, pa3, l3)
    B_refined.show()
    #B_refined.combine_trans()
    #B_refined.show()
    print("--------------------------------------------")
    B_s_refined = RefinedDFA(B_secret, pa3, l3)
    B_s_refined.show()
    #B_s_refined.combine_trans()
    #B_s_refined.show()
    print("--------------------------------------------")
    B_s_C_refined = complementRDFA(B_s_refined)
    B_s_C_refined.show()
    print("--------------------------------------------")
    product = productRDFA(B_refined, B_s_C_refined)
    product.show()
    print("--------------------------------------------")
    productclean = clean_deadstates(product)
    productclean.show()
    print("--------------------------------------------")
    simpledfa = get_simpledfa(productclean)
    simpledfa.show()
    print("--------------------------------------------")
    observable = ['a']
    B_tau = buildBTau(B, observable)
    B_tau.show()
    print("--------------------------------------------")
    Bns_tau = buildBTau(simpledfa, observable)
    Bns_tau.show()

if __name__=='__main__':
	main()    
