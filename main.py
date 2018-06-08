# main func

from projection import *

def main():
    para = sys.argv
    file1 = str(para[1])
    file2 = str(para[2])
    observable = ['a']
    print("------------------System Model--------------------")
    A = buildRTA(file1)
    A.show()
    print("------------------Secret Model-------------------------")
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


