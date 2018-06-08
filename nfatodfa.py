# the projection may be a nfa
# nfa to dfa

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
    temp_state = [copy.deepcopy(nfa.initstate_name)]
    temp_statelist = [temp_state]
    new_statelist = [temp_state]
    while len(new_statelist) > 0:
        new_state = copy.deepcopy(new_statelist[0])
        new_statelist.pop(0)
        f[new_state] = {}
        for label in sigma:
            label_targetlist = []
            for tran in nfa.trans:
                if tran.source in temp_state and label in tran.timedlabel:
                    if tran.target not in label_targetlist:
                        label_targetlist.append(tran.target)
            f[new_state][label] = label_targetlist
            if not islistin(label_targetlist, new_statelist):
                new_statelist.append(label_targetlist)
                temp_statelist.append(label_targetlist)
    states = []
    statename_value = {}
    value_statename = {}
    for state in f:
        init = False
        accept = False
        for term in state:
            if term == nfa.initstate_name:
                init = True
            if term in nfa.accept_names:
                accept = True
        new_state = State(str(len(states)+1), init, accept)
        statename_value[str(len(states)+1)] = state
        value_statename[state] = str(len(states)+1)
        states.append(new_state)
    trans = []
    for state in f:
        new_source = value_statename[state]
        for label in f[state]:
            if len(f[state][label])>0:
                new_target = value_statename[f[state][label]]
                
    
            
                
                    
            
