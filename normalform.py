#define normal form

from projection import *

class NForm:
    def __init__(self, x1, x2, k, N):
        self.x1 = x1
        self.x2 = x2
        self.k = k
        self.N = N

class WNForm:
    def __init__(self, x1, x2, k):
        self.x1 = x1
        self.x2 = x2
        self.k = k

def gcd(a, b):  
    #assert a > 0 and b > 0,'parameters must be greater than 0.'     
    while True:  
        if a >= b:  
            if a % b == 0:  
                return b  
            else:  
                a, b = a - b, b  
        else:  
            a, b = b, a  
  
def lcm(a, b):  
    #assert a > 0 and b > 0,'parameters must be greater than 0.'  
    return int(a * b / gcd(a, b))

def intersect_constraint(c1, c2):
    min_bn1 = None
    max_bn1 = None
    if c1.closed_min == True:
        min_bn1 = BracketNum(c1.min_value, Bracket.LC)
    else:
        min_bn1 = BracketNum(c1.min_value, Bracket.LO)
    if c1.closed_max == True:
        max_bn1 = BracketNum(c1.max_value, Bracket.RC)
    else:
        max_bn1 = BracketNum(c1.max_value, Bracket.RO)
    min_bn2 = None
    max_bn2 = None
    if c2.closed_min == True:
        min_bn2 = BracketNum(c2.min_value, Bracket.LC)
    else:
        min_bn2 = BracketNum(c2.min_value, Bracket.LO)
    if c2.closed_max == True:
        max_bn2 = BracketNum(c2.max_value, Bracket.RC)
    else:
        max_bn2 = BracketNum(c2.max_value, Bracket.RO)
    bnlist = [min_bn1, max_bn1, min_bn2, max_bn2]
    bnlist.sort()
    left_bn = bnlist[1]
    right_bn = bnlist[2]
    if left_bn in [min_bn1, min_bn2] and right in [max_bn1, max_bn2]:
        return Constraint(left_bn.getbn()+','+right_bn.getbn()), True
    else:
        return Constraint("(0,0)"), False

def unintersect_intervals(uintervals):
    unintersect = []
    floor_bn = BracketNum('0',Bracket.LC)
    ceil_bn = BracketNum('+',Bracket.RO)
    key_bns = []
    for constraint in uintervals:
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
    for index in range(len(key_bnsc)):
        if index%2 == 0:
            temp_constraint = Constraint(key_bnsc[index].getbn()+','+key_bnsc[index+1].getbn())
            unintersect.append(constraint)
    return unintersect

def union_intervals_to_nform(uintervals):
    if len(uintervals) >= 1:
        x1 = unintersect_intervals(uintervals)
        k = 1
        constraint = x1[len(x1)-1]
        N = None
        x2 = []
        if constraint.max_value == '+':
            N = int(constraint.min_value)+1
            left,_ = constraint.guard.split(',')
            right = str(N) + ')'
            new_constraint = Constraint(left+','+right)
            x1 = x1[:-1]
            x1.append(new_constraint)
            x2.append(Constraint('['+str(N)+','+str(N+1)+')'))
        else:
            N = int(constraint.max_value)+1
        return NForm(x1,x2,k,N)

def nform_union(X, Y):
    m = lcm(X.k, Y.K)
    new_x1 = []
    new_x1.extend(X.x1)
    new_x1.extend(Y.x1)
    new_x1 = unintersect_intervals(new_x1)
    m_k_1 = m/X.k - 1
    m_l_1 = m/Y.k - 1
    new_x2 = []
    for i in range(m_k_1 + 1):
        k_constraint = Constraint('['+str(i * X.k)+','+str(i * X.k)+']')
        for constraint in X.x2:
            new_constraint = add_constraints(constraint, k_constraint)
            new_x2.append(new_constraint)
    for i in range(m_l_1 + 1):
        l_constraint = Constraint('['+str(i * Y.k)+','+str(i * Y.k)+']')
        for constraint in Y.x2:
            new_constraint = add_constraints(constraint, l_constraint)
            new_x2.append(new_constraint)
    new_x2 = unintersect_intervals(new_x2)
    return WNForm(new_x1, new_x2, m)


        
