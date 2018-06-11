#projection
import sys
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

def delete_unobser(simpledfa, observable):
    obser_trans = []
    for tran in simpledfa.trans:
        if tran.timedlabel.label in observable:
            tran.id = len(obser_trans)
            obser_trans.append(tran)
    simpledfa.trans = obser_trans
    return simpledfa

def add_constraints(c1, c2):
    temp_min_value = ""
    temp_max_value = ""
    if c1.min_value == '+' or c2.min_value == '+':
        temp_min_value = '+'
    else:
        temp_min_value = str(int(c1.min_value) + int(c2.min_value))
    if c1.max_value == '+' or c2.max_value == '+':
        temp_max_value = '+'
    else:
        temp_max_value = str(int(c1.max_value) + int(c2.max_value))
    temp_closed_min = '('
    temp_closed_max = ')'
    if c1.closed_min == True and c2.closed_min == True:
        temp_closed_min = '['
    if c1.closed_max == True and c2.closed_max == True:
        temp_closed_max = ']'
    guard = temp_closed_min + temp_min_value + ',' + temp_max_value + temp_closed_max
    return Constraint(guard)

def get_unobser_interval(btau):
    n = len(btau.states)
    intervals = [[[] for col in range(n)] for row in range(n)]
    for s_i,i in zip(btau.states, range(0,n)):
        for s_j,j in zip(btau.states, range(0,n)):
            temp_source = s_i.name
            temp_target = s_j.name
            for tran in btau.trans:
                if temp_source == tran.source and temp_target == tran.target:
                    if tran.timedlabel.constraints[0] not in intervals[i][j]:
                        intervals[i][j].append(tran.timedlabel.constraints[0])
    for k in range(0, n):
        for i in range(0, n):
            for j in range(0, n):
                new_intervals = []
                for c1 in intervals[i][k]:
                    for c2 in intervals[k][j]:
                        temp_interval = add_constraints(c1,c2)
                        if temp_interval not in new_intervals:
                            new_intervals.append(temp_interval)
                intervals[i][j]= intervals[i][j] + new_intervals
    return intervals

def get_new_unobser_trans(btau, intervals):
    unobser_trans = []
    for i in range(0, len(intervals)):
        for j in range(0, len(intervals)):
            if btau.states[i].init == True and btau.states[j].accept == True:
                if len(intervals[i][j])>0:
                    source_state = btau.states[i].name
                    target_state = btau.states[j].name
                    for constraint in intervals[i][j]:
                        new_timedlabel = TimedLabel("", "Tau", [constraint])
                        new_tran = DFATran(len(unobser_trans), source_state, target_state, new_timedlabel)
                        unobser_trans.append(new_tran)
    return unobser_trans
 
def get_new_obser_trans(simpledfa, unobser_trans):
    index = len(simpledfa.trans)
    new_trans = []
    for ut in unobser_trans:
        new_source = ut.target
        for tran in simpledfa.trans:
            if tran.source == new_source:
                new_target = tran.target
                new_constraint = add_constraints(ut.timedlabel.constraints[0], tran.timedlabel.constraints[0])
                new_timedlabel = TimedLabel("", tran.timedlabel.label, [new_constraint])
                new_tran = DFATran(index, ut.source, tran.target, new_timedlabel)
                new_trans.append(new_tran)
    return new_trans

def projection(simpledfa, new_trans):
    simpledfa.trans = simpledfa.trans + new_trans
    state_names = []
    new_states = []
    temp_alphabet = []
    sigma = []
    accept_names = []
    for tran in simpledfa.trans:
        label = tran.timedlabel.label
        if label not in sigma:
           sigma.append(label)
        if tran.timedlabel not in temp_alphabet:
            temp_alphabet.append(tran.timedlabel)
        if tran.source not in state_names:
            state_names.append(tran.source)
        if tran.target not in state_names:
            state_names.append(tran.target)
    for s in simpledfa.states:
        if s.name in state_names:
            new_states.append(s)
            if s.accept == True:
                accept_names.append(s.name)
    simpledfa.states = new_states
    timed_alphabet = alphabet_classify(temp_alphabet,sigma)
    simpledfa.timed_alphabet = timed_alphabet
    simpledfa.accept_names = accept_names
    return simpledfa

def rename_states(bns):
    state_names = [s.name for s in bns.states]
    for tran in bns.trans:
        tran.source = str(state_names.index(tran.source)+1)
        tran.target = str(state_names.index(tran.target)+1)
    bns.initstate_name = str(state_names.index(bns.initstate_name)+1)
    for sn in bns.accept_names:
        bns.accept_names[state_names.index(sn)] = str(state_names.index(sn)+1)
    for s in bns.states:
        s.name = str(state_names.index(s.name)+1)
    return bns

def main():
    para = sys.argv
    file1 = str(para[1])
    file2 = str(para[2])
    observable = ['a']
    #A = buildRTA("a.json")
    A = buildRTA(file1)
    A.show()
    print("-------------------------------------------")
    #A_secret = buildRTA("a_secret.json")
    A_secret = buildRTA(file2)
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
    Bns_simpledfa = get_simpledfa(productclean)
    Bns_simpledfa.show()
    print("--------------------------------------------")
    B_tau = buildBTau(B, observable)
    B_tau.show()
    print("--------------------------------------------")
    Bns_tau = buildBTau(Bns_simpledfa, observable)
    Bns_tau.show()
    print("--------------------------------------------")
    B_u_intervals = get_unobser_interval(B_tau)
    Bns_u_intervals = get_unobser_interval(Bns_tau)
    """
    for i in range(0, len(B_u_intervals)):
        for j in range(0, len(B_u_intervals)):
            if len(B_u_intervals[i][j])>0:
                print i, '->', j
                for constraints in B_u_intervals[i][j]:
                    print constraints.guard
    """
    print("--------------------------------------------")
    B_u_trans = get_new_unobser_trans(B_tau, B_u_intervals)
    Bns_u_trans = get_new_unobser_trans(Bns_tau, Bns_u_intervals)
    """
    for tran in B_u_trans:
        print tran.id, tran.source, tran.timedlabel.get_timedlabel(), tran.target
    """
    print("--------------------------------------------")
    obser_B = delete_unobser(B, observable)
    obser_Bns = delete_unobser(Bns_simpledfa, observable)
    B_new_trans = get_new_obser_trans(obser_B, B_u_trans)
    Bns_new_trans = get_new_obser_trans(obser_Bns, Bns_u_trans)
    projection_B = projection(obser_B, B_new_trans)
    projection_Bns = projection(obser_Bns, Bns_new_trans)
    projection_B.show()
    print("--------------------------------------------")
    projection_Bns.show()
    print("************************************************")
    projection_Bns = rename_states(projection_Bns)
    projection_Bns.show()
    print("************************************************")
    pa1,l1 = alphabet_partition(projection_B.timed_alphabet)
    pa2,l2 = alphabet_partition(projection_Bns.timed_alphabet)
    pa3,l3 = alphabet_partition(alphabet_combine(projection_B.timed_alphabet, pa2))
    projection_B_refined = RefinedDFA(projection_B, pa3, l3)
    projection_B_refined.show()
    print("************************************************")
    projection_Bns_refined = RefinedDFA(projection_Bns, pa3, l3)
    projection_Bns_refined.show()
    print("************************************************")
    projection_Bns_C_refined = complementRDFA(projection_Bns_refined)
    projection_Bns_C_refined.show()
    print("************************************************")
    new_product = productRDFA(projection_B_refined, projection_Bns_C_refined)
    new_product.show()

if __name__=='__main__':
	main()    
