#definitions
import json

global MAXVALUE
MAXVALUE = 10000

class State:
    name = ""
    init = False
    accept = False
    def __init__(self, name="", init=False, accept=False):
        self.name = name
        self.init = init
        self.accept = accept

class Constraint:
    guard=None
    min_value = ""
    closed_min = True
    max_value = ""
    closed_max = True
    def __init__(self, guard=None):
        self.guard = guard
        self.__build()
    
    def __build(self):
        min_type, max_type = self.guard.split(',')
        if min_type[0] == '[':
            self.closed_min = True
        else:
            self.closed_min = False
        self.min_value = min_type[1:].strip()
        if max_type[-1] == ']':
            self.closed_max = True
        else:
            self.closed_max = False
        self.max_value = max_type[:-1].strip()
    
    def __eq__(self, constraint):
        if self.min_value == constraint.min_value and self.closed_min == constraint.closed_min and self.max_value == constraint.max_value and self.closed_max == constraint.closed_max:
            return True
        else:
            return False
        
    def get_min(self):
        return int(self.min_value)
    
    def get_max(self):
        if self.max == '+':
            closed_max=False
            return MAXVALUE
        else:
            return int(self.max_value)
    
    def get_constraint(self):
        return self.guard

class RTATran:
    id = None
    source = ""
    target = ""
    label = ""
    constraint = None
    def __init__(self, id, source="", target="", label="", constraint=None):
        self.id = id
        self.source = source
        self.target = target
        self.label = label
        self.constraint = constraint
    
class RTA:
    def __init__(self, name="", sigma= None, states=None, trans=None, initstate=None, accept=None):
        self.name = name
        self.sigma = sigma
        self.states = states or []
        self.trans = trans or []
        self.initstate_name = initstate
        self.accept_names = accept or []
    
    def show(self):
        print self.name
        print self.sigma, len(self.sigma)
        for s in self.states:
            print s.name, s.init, s.accept
        for t in self.trans:
            print t.id, t.source, t.label, t.target, t.constraint.guard, t.constraint.min_value, t.constraint.closed_min, t.constraint.max_value, t.constraint.closed_max
        print self.initstate_name
        print self.accept_names

def buildRTA(jsonfile):
    data = json.load(open(jsonfile,'r'))
    name = data["name"].encode("utf-8")
    states_list = [s.encode("utf-8") for s in data["s"]]
    sigma = [s.encode("utf-8") for s in data["sigma"]]
    trans_set = data["tran"]
    initstate = data["init"].encode("utf-8")
    accept_list = [s.encode("utf-8") for s in data["accept"]]
    
    S = [State(state) for state in states_list]
    for s in S:
        if s.name == initstate:
            s.init = True
        if s.name in accept_list:
            s.accept = True
      
    trans = []
    for tran in trans_set:
        tran_id = tran.encode("utf-8")
        source = trans_set[tran][0].encode("utf-8")
        label = trans_set[tran][1].encode("utf-8")
        constraint = Constraint(trans_set[tran][2].encode("utf-8"))
        target = trans_set[tran][3].encode("utf-8")
        rta_tran = RTATran(tran_id, source, target, label, constraint)
        trans += [rta_tran]
    
    return RTA(name, sigma, S, trans, initstate, accept_list)

def main():
    A = buildRTA("a.json")
    A.show()
    print("-------------------------------------------")
    A_secret = buildRTA("a_secret.json")
    A_secret.show()
    
    c1 = Constraint("[2,3]")
    c2 = Constraint("[2,3]")
    c3 = Constraint("[1,3]")
    c4 = Constraint("[2,3)")
    print c1==c2, c1==c3, c1==c4
    """print rta.name
    for s in rta.states:
        print s.name, s.init, s.accept
    for t in rta.trans:
        print t.id, t.source, t.label, t.target, t.constraint.guard, t.constraint.min_value, t.constraint.closed_min, t.constraint.max_value, t.constraint.closed_max
    print rta.initstate_name
    print rta.accept_names"""

if __name__=='__main__':
	main()

    
