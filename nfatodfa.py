# the projection may be a nfa
# nfa to dfa

from projection import *
import time

def listeq(l1, l2):
    if len(l1) == len(l2):
        for t1 in l1:
            if t1 not in l2:
                return False
        for t2 in l2:
            if t2 not in t1:
                return False
        return True
    else:
        return False

def islistin(l, ll):
    for temp_list in ll:
        if listeq(temp_list, l):
            return True
    return False

def nfa_to_dfa(nfa):
    sigma = []
    for term in nfa.timed_alphabet:
        for timedlabel in nfa.timed_alphabet[term]:
            sigma.append(timedlabel.name)
    f = {}
    statename_value = {}
    value_statename = {}
    temp_state = [copy.deepcopy(nfa.initstate_name)]
    temp_statelist = [temp_state]
    new_statelist = copy.deepcopy(temp_statelist)
    index = 0
    while len(new_statelist) > 0:
        new_state = copy.deepcopy(new_statelist[0])
        index = index + 1
        state_name = str(index)
        #print state_name
        statename_value[state_name] = new_state
        new_statelist.pop(0)
        f[state_name] = {}
        for label in sigma:
            label_targetlist = []
            for tran in nfa.trans:
                if tran.source in new_state and label in tran.timedlabel:
                    if tran.target not in label_targetlist:
                        label_targetlist.append(tran.target)
            f[state_name][label] = label_targetlist
            #if not islistin(label_targetlist, temp_statelist):
            if label_targetlist not in temp_statelist:
                if len(label_targetlist)>0:
                    #print label_targetlist
                    new_statelist.append(label_targetlist)
                    temp_statelist.append(label_targetlist)
                    #print len(temp_statelist)
    states = []
    for statename in f:
        init = False
        accept = False
        for term in statename_value[statename]:
            if term == nfa.initstate_name:
                init = True
            if term in nfa.accept_names:
                accept = True
        new_state = State(statename, init, accept)
        #value_statename[state] = str(len(states)+1)
        states.append(new_state)

    for statename in f:
        for label in f[statename]:
            for key in statename_value:
                if f[statename][label] == statename_value[key]:
                    f[statename][label] = key
    """
    for key in f:
        print key
        for label in f[key]:
            print label, f[key][label]
    """
    trans = []
    for statename in f:
        new_source = statename
        label_target = {}
        target_label = {}
        for label in f[statename]:
            if not label_target.has_key(label):
                label_target[label] = []
            if len(f[statename][label])>0:
                new_target = f[statename][label]
                if not target_label.has_key(new_target):
                    target_label[new_target] = []
                    target_label[new_target].append(label)
                else:
                    target_label[new_target].append(label)
        for target in target_label:
            new_timedlabel = target_label[target]
            new_tran = DFATran(len(trans), new_source, target, sorted(new_timedlabel))
            trans.append(new_tran)
    initstate_name = ""
    accept_names = []
    for s in states:
        if s.init == True:
            initstate_name = s.name
        if s.accept == True:
            accept_names.append(s.name)
    timed_alphabet = copy.deepcopy(nfa.timed_alphabet)
    return CRDFA(nfa.name, timed_alphabet, states, trans, initstate_name, sorted(accept_names)), statename_value

def main():
    #para = sys.argv
    #file1 = str(para[1])
    #file2 = str(para[2])
    start = time.time()
    observable = ['a']
    A = buildRTA("a.json")
    #A = buildRTA(file1)
    #A.show()
    print("-------------------------------------------")
    A_secret = buildRTA("a_secret.json")
    #A_secret = buildRTA(file2)
    #A_secret.show()
    print("-------------------------------------------")
    B = DFA(A, "generation")
    #B.show()
    #for timed_label in B.timed_alphabet["a"]:
    #    print timed_label.get_timedlabel()
    print("-------------------------------------------")
    B_secret = DFA(A_secret, "receiving")
    #B_secret.show()
    #for timed_label in B_secret.timed_alphabet["b"]:
    #    print timed_label.get_timedlabel()
    print("---------------------------------------------")
    pa1,l1 = alphabet_partition(B.timed_alphabet)
    pa2,l2 = alphabet_partition(B_secret.timed_alphabet)
    pa3,l3 = alphabet_partition(alphabet_combine(B.timed_alphabet, pa2))
    """
    for term in pa3:
        for timedlabel in pa3[term]:
            print timedlabel.name, timedlabel.get_timedlabel()
    for term in l3:
        for bn,index in zip(l3[term],range(len(l3[term]))):
            print index, bn.getbn()
    """
    print("--------------------------------------------")
    B_refined = RefinedDFA(B, pa3, l3)
    #B_refined.show()
    #B_refined.combine_trans()
    #B_refined.show()
    print("--------------------------------------------")
    B_s_refined = RefinedDFA(B_secret, pa3, l3)
    #B_s_refined.show()
    #B_s_refined.combine_trans()
    #B_s_refined.show()
    print("--------------------------------------------")
    B_s_C_refined = complementRDFA(B_s_refined)
    #B_s_C_refined.show()
    print("--------------------------------------------")
    product = productRDFA(B_refined, B_s_C_refined)
    #product.show()
    print("--------------------------------------------")
    productclean = clean_deadstates(product)
    #productclean.show()
    print("--------------------------------------------")
    Bns_simpledfa = get_simpledfa(productclean)
    #Bns_simpledfa.show()
    print("--------------------------------------------")
    B_tau = buildBTau(B, observable)
    #B_tau.show()
    print("--------------------------------------------")
    Bns_tau = buildBTau(Bns_simpledfa, observable)
    #Bns_tau.show()
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
    #projection_B.show()
    print("--------------------------------------------")
    #projection_Bns.show()
    print("--------------------------------------------")
    projection_Bns = rename_states(projection_Bns)
    #projection_Bns.show()
    print("************************************************")
    pa1,l1 = alphabet_partition(projection_B.timed_alphabet)
    pa2,l2 = alphabet_partition(projection_Bns.timed_alphabet)
    pa3,l3 = alphabet_partition(alphabet_combine(projection_B.timed_alphabet, pa2))
    projection_B_refined = RefinedDFA(projection_B, pa3, l3)
    #projection_B_refined.show()
    print("************************************************")
    projection_Bns_refined = RefinedDFA(projection_Bns, pa3, l3)
    #projection_Bns_refined.show()
    print("*****************dfa*************************")
    dfa_projection_B, _ = nfa_to_dfa(projection_B_refined)
    #dfa_projection_B.show()
    print("*****************dfa*************************")
    dfa_projection_Bns, _ = nfa_to_dfa(projection_Bns_refined)
    #dfa_projection_Bns.show()
    
    print("************************************************")
    dfa_projection_Bns_C_refined = complementRDFA(dfa_projection_Bns)
    #dfa_projection_Bns_C_refined.show()
    print("************************************************")
    new_product = productRDFA(dfa_projection_B, dfa_projection_Bns_C_refined)
    end = time.time()
    new_product.show()
    print end - start
if __name__=='__main__':
	main()     
            
                
                    
            
