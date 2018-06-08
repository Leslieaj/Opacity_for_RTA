# build a kind of DFA which moves the guards of RTA into the labels

import copy
from enum import IntEnum
from rta import *

class Bracket(IntEnum):
    """
    Left Open, Left Closed, Right Open, Right Closed.
    """
    RO = 1
    LC = 2
    RC = 3
    LO = 4

class BracketNum:
    def __init__(self, value="", bracket=0):
        self.value = value
        self.bracket = bracket
    def __eq__(self, bn):
        if self.value == bn.value and self.bracket == bn.bracket:
            return True
        else:
            return False
    def __lt__(self, bn):
        if self.value == '+':
            return False
        if bn.value == '+':
            return True
        if int(self.value) > int(bn.value):
            return False
        elif int(self.value) < int(bn.value):
            return True
        else:
            if self.bracket < bn.bracket:
                return True
            else:
                return False
    def complement(self):
        if self.value == '+':
            return BracketNum('+', Bracket.RO)  #ceil
        if self.value == '0' and self.bracket == Bracket.LC:
            return BracketNum('0', Bracket.LC)  #floor
        temp_value = self.value
        temp_bracket = None
        if self.bracket == Bracket.LC:
            temp_bracket = Bracket.RO
        if self.bracket == Bracket.RC:
            temp_bracket = Bracket.LO
        if self.bracket == Bracket.LO:
            temp_bracket = Bracket.RC
        if self.bracket == Bracket.RO:
            temp_bracket = Bracket.LC
        return BracketNum(temp_value, temp_bracket)
    
    def getbn(self):
        temp_value = self.value
        if self.bracket == Bracket.LC:
            return '[' + self.value
        if self.bracket == Bracket.LO:
            return '(' + self.value
        if self.bracket == Bracket.RC:
            return self.value + ']'
        if self.bracket == Bracket.RO:
            return self.value + ')'

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
    def __eq__(self, timedlabel):
        if self.label == timedlabel.label and self.get_timedlabel() == timedlabel.get_timedlabel():
            return True
        else:
            return False

class DFATran:
    id = None
    source = ""
    target = ""
    timedlabel = None
    def __init__(self, id, source="", target="", label=None):
        self.id = id
        self.source = source
        self.target = target
        self.timedlabel = label

class DFA:
    name = ""
    #timed_alphabet = None
    timed_alphabet = {}
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

def alphabet_partition(classified_alphabet):
    floor_bn = BracketNum('0',Bracket.LC)
    ceil_bn = BracketNum('+',Bracket.RO)
    partitioned_alphabet = {}
    bnlist_dict = {}
    for key in classified_alphabet:
        partitioned_alphabet[key] = []
        timedlabel_list = classified_alphabet[key]
        key_bns = []
        key_bnsc = []
        for timedlabel in timedlabel_list:
            temp_constraints = timedlabel.constraints
            for constraint in temp_constraints:
                min_bn = None
                max_bn = None
                temp_min = constraint.min_value
                temp_minb = None
                if constraint.closed_min == True:
                    temp_minb = Bracket.LC
                else:
                    temp_minb = Bracket.LO
                temp_max = constraint.max_value
                temp_maxb = None
                if constraint.closed_max == True:
                    temp_maxb = Bracket.RC
                else:
                    temp_maxb = Bracket.RO
                min_bn = BracketNum(temp_min, temp_minb)
                max_bn = BracketNum(temp_max, temp_maxb)
                if min_bn not in key_bns:
                    key_bns+= [min_bn]
                if max_bn not in key_bns:
                    key_bns+=[max_bn]
        #print("------------------------------------")
        #for i in key_bns:
            #print key, i.getbn()
        key_bnsc = copy.deepcopy(key_bns)
        for bn in key_bns:
            bnc = bn.complement()
            if bnc not in key_bnsc:
                key_bnsc.append(bnc)
        if floor_bn not in key_bnsc:
            key_bnsc.append(floor_bn)
        if ceil_bn not in key_bnsc:
            key_bnsc.append(ceil_bn)
        key_bnsc.sort()
        bnlist_dict[key] = key_bnsc
        for index in range(len(key_bnsc)):
            if index%2 == 0:
                temp_constraint = Constraint(key_bnsc[index].getbn()+','+key_bnsc[index+1].getbn())
                temp_timedlabel = TimedLabel("",key, [temp_constraint])
                partitioned_alphabet[key].append(temp_timedlabel)
    for term in partitioned_alphabet:
        for timedlabel,index in zip(partitioned_alphabet[term], range(len(partitioned_alphabet[term]))):
            timedlabel.name = term + '_'+ str(index)
    return partitioned_alphabet, bnlist_dict

def alphabet_combine(alphabet1, alphabet2):
    """
    They have same simple alphabet.
    """
    combined_alphabet = {} 
    for key in alphabet1:
        combined_alphabet[key] = alphabet1[key] + alphabet2[key]
    return combined_alphabet

class RefinedDFA:
    name = ""
    timed_alphabet = {}
    states = None
    trans = []
    initstate_name = ""
    accept_names = []
    def __init__(self, dfa=None, partition_alphabet=None, bnlist_dict=None):
        self.name = "Refined_"+dfa.name
        self.timed_alphabet = partition_alphabet
        self.states = dfa.states
        self.initstate_name = dfa.initstate_name
        self.accept_names = dfa.accept_names
        self.trans = self.__buildtrans(dfa, bnlist_dict)
    def __buildtrans(self, dfa, bnlist_dict):
        temp_trans = []
        for tran in dfa.trans:
            temp_refinedlabel = []
            temp_timedlabel = tran.timedlabel
            temp_constraints = temp_timedlabel.constraints
            temp_left = 0
            temp_right = 0
            for constraint in temp_constraints:
                min_bn = None
                max_bn = None
                temp_min = constraint.min_value
                temp_minb = None
                if constraint.closed_min == True:
                    temp_minb = Bracket.LC
                else:
                    temp_minb = Bracket.LO
                temp_max = constraint.max_value
                temp_maxb = None
                if constraint.closed_max == True:
                    temp_maxb = Bracket.RC
                else:
                    temp_maxb = Bracket.RO
                min_bn = BracketNum(temp_min, temp_minb)
                max_bn = BracketNum(temp_max, temp_maxb)
                for bn, index in zip(bnlist_dict[temp_timedlabel.label], range(len(bnlist_dict[temp_timedlabel.label]))):
                    if min_bn == bn:
                        temp_left = index
                    if max_bn == bn:
                        temp_right = index
            index_begin = temp_left//2
            index_end = temp_right//2
            temp_refinedlabel = [temp_timedlabel.label+'_'+str(index) for index in range(index_begin, index_end+1)]
            dfa_tran = DFATran(tran.id, tran.source, tran.target, temp_refinedlabel)
            temp_trans.append(dfa_tran)
        return temp_trans
    def combine_trans(self):
        temp_trans = []
        for tran in self.trans:
            flag = False
            if len(temp_trans) == 0:
                temp_trans.append([tran])
                flag = True
                continue
            for tran_list in temp_trans:
                if tran_list[0].source == tran.source and tran_list[0].target == tran.target:
                    tran_list.append(tran)
                    flag = True
                    break
            if flag == False:
                temp_trans.append([tran])
                flag = True
        #print len(temp_trans)
        combined_trans = []
        for tran_list in temp_trans:
            temp_timedlabel = []
            temp_source = tran_list[0].source
            temp_target = tran_list[0].target
            temp_id = temp_trans.index(tran_list)
            for tran in tran_list:
                temp_timedlabel += tran.timedlabel
            dfa_tran = DFATran(temp_id, temp_source, temp_target, temp_timedlabel)
            combined_trans.append(dfa_tran)
        self.trans = combined_trans
                
    def show(self):
        print self.name
        for term in self.timed_alphabet:
            for timedlabel in self.timed_alphabet[term]:
                print timedlabel.name, timedlabel.get_timedlabel()
        #print self.timed_alphabet.name, self.timed_alphabet.label, self.timed_alphabet.constraint.guard, len(self.timed_alphabet)
        for s in self.states:
            print s.name, s.init, s.accept
        #print self.trans
        for t in self.trans:
            print t.id, t.source, t.timedlabel, t.target
        print self.initstate_name
        print self.accept_names 

class CRDFA:
    name = ""
    timed_alphabet = {}
    states = None
    trans = []
    initstate_name = ""
    accept_names = []
    def __init__(self, name="", timed_alphabet={}, states=None, trans=[], initstate_name="", accept_names=[]):
        self.name = name
        self.timed_alphabet = timed_alphabet
        self.states = states
        self.trans = trans
        self.initstate_name = initstate_name
        self.accept_names = accept_names
    def show(self):
        print self.name
        for term in self.timed_alphabet:
            for timedlabel in self.timed_alphabet[term]:
                print timedlabel.name, timedlabel.get_timedlabel()
        #print self.timed_alphabet.name, self.timed_alphabet.label, self.timed_alphabet.constraint.guard, len(self.timed_alphabet)
        for s in self.states:
            print s.name, s.init, s.accept
        #print self.trans
        for t in self.trans:
            print t.id, t.source, t.timedlabel, t.target
        print self.initstate_name
        print self.accept_names
 
def complementRDFA(rdfa):
    states_num = len(rdfa.states)
    print states_num
    temp_states = copy.deepcopy(rdfa.states)
    new_state = State(str(states_num+1), False, True)
    flag = False
    temp_trans = copy.deepcopy(rdfa.trans)
    temp_alphabet = copy.deepcopy(rdfa.timed_alphabet)
    temp_initstate = copy.deepcopy(rdfa.initstate_name)
    temp_accepts = []
    for state in temp_states:
        if state.accept == False:
            state.accept = True
            temp_accepts.append(state.name)
        else:
            state.accept = False
    timedlabels_name = []
    source_set = set()
    for term in rdfa.timed_alphabet:
        for timedlabel in rdfa.timed_alphabet[term]:
            timedlabels_name.append(timedlabel.name)
    for s in temp_states:
        #print s.name
        source_set.add(s.name)
        s_trans = []
        for tran in rdfa.trans:
            if s.name == tran.source:
                s_trans.append(tran)
        temp_timedlabel = []
        for tran in s_trans:
            for tl in tran.timedlabel:
                if tl not in temp_timedlabel:
                    temp_timedlabel.append(tl)
        new_tran_timedlabel = []
        for label_name in timedlabels_name:
            if label_name not in temp_timedlabel:
                new_tran_timedlabel.append(label_name)
        if len(new_tran_timedlabel)>0:
            print s.name, new_state.name
            new_tran = DFATran(len(temp_trans), s.name, new_state.name, new_tran_timedlabel)
            temp_trans.append(new_tran)
            print len(temp_trans)
            flag = True
    """
    for tran in rdfa.trans:
        source_set.add(tran.source)
        temp_timedlabel = tran.timedlabel
        new_tran_timedlabel = []
        for label_name in timedlabels_name:
            if label_name not in temp_timedlabel:
                new_tran_timedlabel.append(label_name)
        if len(new_tran_timedlabel)>0:
            new_tran = DFATran(len(temp_trans), tran.source, new_state.name, new_tran_timedlabel)
            temp_trans.append(new_tran)
            flag = True
    """
    if flag == True:
        temp_states.append(new_state)
        temp_accepts.append(new_state.name)
    noout_state = []
    for state in temp_states:
        if state.name not in source_set:
            new_tran = DFATran(len(temp_trans), state.name, new_state.name, timedlabels_name)
            temp_trans.append(new_tran)
    return CRDFA('C_'+rdfa.name, temp_alphabet,temp_states,temp_trans,temp_initstate,temp_accepts)

def productRDFA(rdfa1, rdfa2):
    temp_states = []
    statenames = []
    reach_states = []
    final_states = []
    temp_trans = []
    temp_initname = ""
    temp_accept_names = []
    temp_alphabet = rdfa1.timed_alphabet
    for state1 in rdfa1.states:
        for state2 in rdfa2.states:
            new_state_name = state1.name + '_' + state2.name
            statenames.append(new_state_name)
            new_state_init = False
            new_state_accept = False
            if state1.init == True and state2.init == True:
                new_state_init = True
            if state1.accept == True and state2.accept == True:
                new_state_accept = True
            new_state = State(new_state_name, new_state_init, new_state_accept)
            temp_states.append(new_state)
            if new_state_init == True:
                reach_states.append(new_state)
    while len(reach_states) > 0:
        rstate = reach_states.pop(0)
        statename1, statename2 = rstate.name.split('_')
        for tran1 in rdfa1.trans:
            if tran1.source == statename1:
                target1 = tran1.target
                label1_list = tran1.timedlabel
                for tran2 in rdfa2.trans:
                    if tran2.source == statename2:
                        common_labels = []
                        target2 = tran2.target
                        label2_list = tran2.timedlabel
                        for label1 in label1_list:
                            for label2 in label2_list:
                                if label1 == label2:
                                    common_labels.append(label1)
                        targetname = target1+'_'+target2
                        if len(common_labels)>0:
                            for state in temp_states:
                                if state.name == targetname:
                                    if state not in reach_states:
                                        reach_states.append(state)
                            new_tran = DFATran(len(temp_trans), rstate.name, targetname, common_labels)
                            temp_trans.append(new_tran)
        final_states.append(rstate)
    for state in final_states:
        if state.init == True:
            temp_initstate = state.name
        if state.accept == True:
            temp_accept_names.append(state.name)
        #print state.name, state.init, state.accept
    return CRDFA("P_"+rdfa1.name+'-'+rdfa2.name, temp_alphabet, final_states, temp_trans, temp_initstate, temp_accept_names)

def has_deadstates(dfa):
    source_states = []
    for tran in dfa.trans:
        if tran.source not in source_states:
            source_states.append(tran.source)
    dead_states = []
    for s in dfa.states:
        if s.name not in source_states:
            if s.accept == False:
                dead_states.append(s)
    return len(dead_states)
          
def clean_deadstates(dfa):
    cleandfa = copy.deepcopy(dfa)
    source_states = []
    for tran in cleandfa.trans:
        if tran.source not in source_states:
            source_states.append(tran.source)
    dead_states = []
    for s in cleandfa.states:
        if s.name not in source_states:
            if s.accept == False:
                dead_states.append(s)
                cleandfa.states.remove(s)
    dead_statesname = [s.name for s in dead_states]
    for tran in cleandfa.trans:
        if tran.target in dead_statesname:
            cleandfa.trans.remove(tran)
    if has_deadstates(cleandfa) > 0:
        clean_deadstates(cleandfa)
    else:
        return cleandfa

class SimpleDFA:
    def __init__(self, name, states, timed_alphabet, trans, initstates, accept):
        self.name = name
        self.states = states
        self.timed_alphabet = timed_alphabet
        self.states = states
        self.trans = trans
        self.initstate_name = initstates
        self.accept_names = accept
    def show(self):
        #print self.name
        for term in self.timed_alphabet:
            #print len(self.timed_alphabet[term])
            for timedlabel in self.timed_alphabet[term]:
                print timedlabel.get_timedlabel()
        #print self.timed_alphabet.name, self.timed_alphabet.label, self.timed_alphabet.constraint.guard, len(self.timed_alphabet)
        for s in self.states:
            print s.name, s.init, s.accept
        for t in self.trans:
            print t.id, t.source, t.timedlabel.get_timedlabel(), t.target
        print self.initstate_name
        print self.accept_names   

def add_partitions(p1, p2):
    left_p1, right_p1 = p1.guard.split(',')
    left_p2, right_p2 = p2.guard.split(',')
    if p1.max_value == p2.min_value:
        return Constraint(left_p1+','+right_p2)
    if p2.max_value == p1.min_value:
        return Constraint(left_p2+','+right_p1)
    return p1

def refinetrans(dfa):
    trans = []
    temp_alphabet = []
    sigma = []
    for tran,index in zip(dfa.trans,range(0,len(dfa.trans))):
        if len(tran.timedlabel) >= 1:
            label,_ = tran.timedlabel[0].split('_')
            if label not in sigma:
                sigma.append(label)
            partitions = []
            new_tran_constraint = None
            for temp in dfa.timed_alphabet[label]:
                if temp.name in tran.timedlabel:
                    partitions.append(copy.deepcopy(temp))
            if len(partitions) == 1:
                new_tran_constraint = partitions[0].constraints[0]
            if len(partitions) > 1:
                new_tran_constraint = partitions[0].constraints[0]
                for i in range(1, len(partitions)):
                    new_tran_constraint = add_partitions(new_tran_constraint, partitions[i].constraints[0])
            new_timedlabel = TimedLabel("", label, [new_tran_constraint])
            if new_timedlabel not in temp_alphabet:
                temp_alphabet.append(new_timedlabel)
            new_tran = DFATran(index, tran.source, tran.target, new_timedlabel)
            trans.append(new_tran)
    timed_alphabet = alphabet_classify(temp_alphabet,sigma)
    return trans, timed_alphabet

def get_simpledfa(dfa):
    states = copy.deepcopy(dfa.states)
    trans, timed_alphabet = refinetrans(dfa)
    #print len(timed_alphabet)
    initstates = dfa.initstate_name
    accept = dfa.accept_names
    return SimpleDFA("", states, timed_alphabet, trans, initstates, accept)

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
    """
    temp_trans = refinetrans(productclean)
    for tran in temp_trans:
        print tran.id, tran.source, tran.timedlabel.get_timedlabel(), tran.target
    
    bn1 = BracketNum("+", Bracket.LC)
    bn2 = BracketNum("+", Bracket.LO)
    bn3 = bn1.complement()
    bn4 = BracketNum("1", Bracket.LO)
    bn_list = [bn1,bn2,bn3]
    print bn1 < bn2
    print bn1.getbn(), bn2.getbn(), bn3.getbn()
    print bn4 not in bn_list
    """


if __name__=='__main__':
	main()          
