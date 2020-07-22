'''
Copyright (c) 2020, Board of Trustees of the University of Iowa.
All rights reserved.

Use of this source code is governed by a BSD 3-Clause License that
can be found in the LICENSE file.
'''

from pysmt.shortcuts import Symbol, And, Or, EqualsOrIff, Implies, Not, get_formula_size, ExactlyOne, FALSE

from edu.uiowa.parser.Formula import PLTLFormula
from edu.uiowa.parser.Tracer import Trace
from itertools import product
from edu.uiowa.solver.RunSolver import SATSolver

import logging


class SATEncoder:
    
    def __init__(self, size, nr_vars, unary_operators, binary_operators, AP_Lit):

#        unary_operators = set(['!', 'Y', 'O', 'H', 'G'])                    
        #size        
        self.d = size
        
        logging.info('Generate Encoding for Formula size %d'%(self.d))
        
#        logging('SELF . D, Size', self.d)
        #variables at each timestep
        self.v = nr_vars
        logging.debug('Size of variables %d'%(self.v))
        
#        if(not self.d >= self.v):
#            logging('Warning! size mismatch b/t nr. of variables & length of formula', self.d, self.v)
#            exit()

        #set AP (v0,v1,v2,...,vn)
        if AP_Lit is None:
            self.AP = set(['p'+str(i) for i in range(0, self.v)])
        else:
            self.AP = set(AP_Lit)
                
        logging.info('Labels set (AP): %s'%(self.AP))
        #PLTL Operators: 
        #'H', 'O', '!', '&','|', 'Y', 'S'
        self.unaryOp = set(unary_operators)
        self.binaryOp = set(binary_operators)
#        print('Binary OPSSS **************',self.binaryOp) 
        self.C = self.unaryOp.union(self.binaryOp)
        
        self.Constants = {'Top', 'Bottom'}
        
        self.AP = self.AP.union(self.Constants)
        
        #Label set L = {P\cup C}
        self.L = self.AP.union(self.C)
        
            
#        self.L = self.L.union(self.Constants)
        
        # DAG Variables
        self.x = {}
        self.l = {}
        self.r = {}
        
        # Instances of variables
        self.x = {(index, label): self.node(index, label) for index in range(1, self.d + 1) for label in self.L}
        logging.debug('Nodes set: %s'%(self.x))
        #l(parent, child)
        self.l = {(p, c): self.left(p, c) for p in range(2, self.d + 1) for c in range(1, p)}
        logging.debug('LEFT Nodes set: %s'%(self.l)) 
        #r(parent, child)
        self.r = {(p, c): self.right(p, c) for p in range(2, self.d + 1) for c in range(1, p)}
        logging.debug('RIGHT Nodes set: %s'%(self.r))
        # Valuation Variable
#        self.y = {}        
#        self.y = {(i, t): Symbol("y_%d_%d" %(i, t)) for i in range(self.d) for t in range(trace.traceLength)}
#        self.y = {(index, timestep): Symbol("y_%d_%d" %(index, timestep)) for index in range(1, self.d) for timestep in range(trace.traceLength)}
     
    def get_vars(self):
        return self.x.values();    

    #xilabel  i\in{1,...,n} and label \in C
    #Node i labeled with Operations in AP \cup C 
    def node(self, i, label):
        assert label in self.L
        if(i >= 1 and i<=self.d):
            return Symbol("x_%d_%s" %(i, label))

        #return FALSE()
    # i left child j
    def left(self, i, j):
        # Node 1 is always a leaf node, labeled with Atomic Proposition, so skipping i = 1
        #children IDs are less than parent, i - 1
        if((i>=2 and i<=self.d) and (j>=1 and j <= (i - 1))):
            return Symbol("l_%d_%d" %(i, j))

    #right child
    def right(self, i,j):
        # Node 1 is always a leaf node, labeled with Atomic Proposition, so skipping i = 1
        if((i>=2 and i<=self.d) and (j>=1 and j <= (i - 1))):
            return Symbol("r_%d_%d" %(i, j))     


    #Encoding DAG G
    def encode_shape(self):
        
        #[@TODO]If p in {Operators} support to perform selective formula creation.
        
        logging.debug('Encoding (Prop) Shape Rules...')

        #a) Each node is labeled with exactly (At Least, At Most) one label (Operator or variable).
        c_1_a = [] # At least constraints
        logging.debug('c_1_a: Each node is labeled with at least one label:')
        
        for i in range(1, self.d + 1):
            c_1_a.append(And([Or(self.x[i, label] for label in self.L)]))
        logging.debug('c_1_a:%s'%(c_1_a))

        c_1_b = [] # At Most Constraints
        #product of label, not reflex and not commutative 
        prod_labels = list(filter(lambda t: t[0] < t[1], product(self.L,self.L)))
        
        logging.debug('c_1_b: Each node is labeled with at most one label:')        
        
        for i in range(1, self.d + 1):
            
            or_cls = []
            for (l,l1) in prod_labels:
                or_cls.append(Or(Not(self.x[i,l]), Not(self.x[i,l1])))
            c_1_b.append(And(or_cls))    

        logging.debug('c_1_b:%s'%(c_1_b))    
    

        c_2 = []
        logging.debug('c_2: Each node is labeled with a binary operator has always (exactly) two outgoing edges:')
        for i in range(2, self.d + 1):
            out_edges = self.aux_out_egdes(i)
            and_cls = []                            
            for label in self.binaryOp:
                or_cls = []
                for (u,v) in out_edges:
#                    logging.debug('%s => %s and %s '%(self.x[i, label], self.l[u], self.r[v]))
                    or_cls.append(And(self.l[u], self.r[v]))
                and_cls.append(Implies(self.x[i, label], ExactlyOne(or_cls)))
            c_2.append(And(and_cls))        
        logging.debug('c_2:%s'%(c_2))


        c_3 = []
        logging.debug('c_3: Each node is labeled with a unary operator has exactly one outgoing edge (Default: Left edge) and no right edge:')            
        # At most constraint
        for i in range(2, self.d + 1):
            out_edges = self.aux_out_egdes(i)
            and_cls = []                            
            for label in self.unaryOp:
                or_cls = []
                right_edge = []                
                for (u,v) in out_edges:
                    if not self.l[u] in or_cls:                     
                        or_cls.append(self.l[u])
                        right_edge.append(Not(self.r[u]))
                and_cls.append(Implies(self.x[i, label], ExactlyOne(or_cls)))
                and_cls.append(Implies(self.x[i, label], And(right_edge)))
#                logging.debug('%s => ExactlyOne(%s) '%(self.x[i, label], ExactlyOne(or_cls)))
            c_3.append(And(and_cls))        
        logging.debug('c_3:%s'%(c_3))
            
            
        #d) each node labeled with AP has no outgoing edge (neither left, nor right)
#        print('****:',self.x)
        logging.debug('c_4: Each node is labeled from AP has no outgoing edge:')                    
        c_4 = []        
        for i in range(2, self.d + 1):
            out_edges = self.aux_out_egdes(i)
            and_cls = []                            
            for label in self.AP:
                or_cls = []                
                for (u,v) in out_edges:
#                    logging.debug('%s => %s and %s '%(self.x[i, label], self.l[u], self.r[v]))
                    or_cls.append(Not(self.l[u]))
                    or_cls.append(Not(self.r[v]))                    
                and_cls.append(Implies(self.x[i, label], And(or_cls)))
            c_4.append(And(and_cls))        
        logging.debug('c_4:%s'%(c_4))

        #e) node 1 is always labeled with AP
        c_5_a = []
        logging.debug('c_5: node 1 is always labeled with at least one label from AP:')
        for label in self.AP:
            c_5_a.append(self.x[1, label])
        logging.debug('c_5_a:%s'%(c_5_a))
        
#        print('++++++++++++++:',c_5_a)
        c_5_b = []
        logging.debug('c_5: node 1 is always labeled with at most one label from AP:')
        prod_labels = list(filter(lambda t: t[0] < t[1], product(self.AP,self.AP)))    

        for (u,v) in prod_labels:
            c_5_b.append(Or(Not(self.x[1, u]), Not(self.x[1,v])))
        
        logging.debug('c_5_b:%s'%(c_5_b))
        
        
        c_6 = []
        #Quite strong replace it with simpler one.
        logging.debug('c_6: Each node labeled with operator has a parent also labeled with the operator:')
        for i in range(2, self.d + 1):
            if i + 1 < self.d+1:
                c_6.append(Implies(self.aux_or_cls(i), self.aux_or_cls(i + 1)))
        logging.debug('c_6: %s'%(c_6))

#        logging('Left', And(c_6))

        c_7 = []
        logging.debug('c_7: Each node has exactly at least incoming edge (except root node):')            
        for i in range(1, self.d+1):
            or_cls = []
            for j in range(i + 1, self.d+1):
                or_cls.append(self.l[j,i])
                or_cls.append(self.r[j,i])
            if len(or_cls) != 0:    
                c_7.append(Or(or_cls))    
        
        logging.debug('c_7: %s'%(c_7))

        #k) Once and Hence rule doesn't come in same succession?
        logging.debug('All rules encoding well-defined pLTL in shape of a (DAG)')            
        
        c_8 = [self.x[self.d,'G']]
        for i in range(1, self.d):
            c_8.append(Not(self.x[i, 'G']))
        
#Verifying particular solution.        
#        c_9 = [self.x[1,'q'], self.x[2,'p'], self.x[3,'Y'], self.x[4,'|'], self.x[5,'O']]   
        
        #Models of ast_enc are pLTL ASTs 
        ast_enc = And(c_1_a) & And(c_1_b) &  And(c_2) & And(c_3) & And(c_4) & Or(c_5_a) & And(c_5_b) & And(c_6)  & And(c_7) & And(c_8) #& And(c_9)
#        ast_enc = ast_enc & self.x[1, 'Top']
        return ast_enc
                
    def aux_out_egdes(self, index):
        
        edges = list(product(range(index, index+1), range(1,index)))
        out_edges = list(product(edges, edges))  
        
        return out_edges
    
    def aux_or_cls(self, index):
        or_cls = []
        for label in self.C:
            or_cls.append(self.x[index,label])        
        return Or(or_cls)    

    def sigma(self, tId, index, timestep):        
        return Symbol("sig_%s_%d_%d" %(tId, index, timestep))
    
    #PLTL Trace Semantics
    #[@TODO]Add Trace ID for each trace?    
    def encode_trace(self, trace, trace_type = True):
        
        logging.debug('Encoding (Prop.) Trace Rules w.r.t. %s'%(trace.Id))
        tId = trace.Id
        #Check.
        if len(trace.literals)+2 != len(self.AP):
            logging.error('Trace Labels and AP size miss match! %d != %d'%(len(trace.literals), len(self.AP)) )
            exit(-1)
        
        sig = {(i, t): self.sigma(tId, i, t) for i in range(1, self.d + 1) for t in range(trace.traceLength)}        
        logging.debug('Trace evaluation function %s'%(sig))        
        
        #remove it afterwards
        logging.debug('%s'%(trace.print_trace()))

        
        logging.debug('[Constant Rule] If a node is labeled with Top or Bottom then sigma, i models TRUE / FALSE iff True / False:')            
        logging.debug('[Prop Rule] If a node is labeled with p then sigma, i models p iff s_i,t is true at position i of the trace:')       
        
#        print('******** Trace Table',trace.table)     
        # Atomic Proposition Rule:
        # If a node (@index [i]) labeled with p then sigma_i_t iff p \in trace(t) else \not sigma_i_t
        prop_rule = []  
        for i in range(1, self.d + 1):
            p_eval = []
            for p in self.AP:
                antecedent = self.x[i, p]
                consequent = []
                for t in range(trace.traceLength):
                    if p == 'Top':
                        consequent.append(sig[i, t])
                    elif p == 'Bottom':
                        consequent.append(Not(sig[i, t]))                        
                    elif trace.table[p, t] == True:
                        consequent.append(sig[i, t])
                    else:
                        consequent.append(Not(sig[i, t]))
#                logging.debug('%s => %s'%(antecedent, consequent))             
                p_eval.append(Implies(antecedent, And(consequent)))
#                p_eval.append(And())
            prop_rule.append(And(p_eval))
        logging.debug('[Prop Rule:]%s'%(prop_rule))        
        #Negation Rule
        logging.debug('[Negation Rule] If a node i has a child j and labeled with ! then sigma(i,t) is the negation of sigma_j_t')            
        #If a node i is labeled with '!', then y_i_t is the negation of y_j_t where j is left child.  
        op = '!' 
        neg_rule = []
        if op in self.unaryOp: 
            for i in range(2, self.d + 1):
                n_eval = []
                for j in range(1, i):
                    antecedent = self.l[i, j]
                    consequent = [] 
                    for t in range(trace.traceLength):
                        consequent.append(EqualsOrIff(sig[i,t], Not(sig[j,t])))   
                    n_eval.append(Implies(antecedent, And(consequent)))
                neg_rule.append(Implies(self.x[i, op], And(n_eval)))
                
            logging.debug('Negation Rule: %s'%(neg_rule))

        #Yesterday Rule
        #Can Support Operator Z by replace instance 0 to Or(sig[j,t], Not(sig[j,t)) from And(sig[j,t], Not(sig[j,t]))
        logging.debug('[Yesterday Rule] If a node i labeled with Y and has a child j then sigma(i,t) is equal to  sigma_j_(t-1)')
        #If a node i is labeled with 'Y', then y_i_t is equals to y_j_(t-1) where j is left child.
        op = 'Y'
        yesterday_rule = []   
        if op in self.unaryOp:     
            for i in range(2, self.d + 1):
                n_eval = []
                for j in range(1, i):
                    antecedent = self.l[i, j]
                    consequent = [] 
                    for t in range(trace.traceLength):
                        y_var = self.aux_yesterday(sig, j, t)
                        logging.debug('%s <=> YESTERDAY(%s)'%(sig[i,t], y_var))                   
                        consequent.append(EqualsOrIff(sig[i,t], y_var))
                    n_eval.append(Implies(antecedent, And(consequent)))
                    logging.debug('%s <=> YESTERDAY(%s)'%(antecedent, consequent))
                yesterday_rule.append(Implies(self.x[i, op], And(n_eval)))
                            
            logging.debug('Yesterday Rule: %s'%(yesterday_rule))
        
        #Once
        logging.debug('[Once Rule] If a node i labeled with O and has a child j then sigma(i,t) is equal to  sigma_j_(0) v sigma_j_(1) v sigma_j_(2) v sigma_j_(t)')
        #Once rule
        #If a node i is labeled wit 'O'), then y_i_t is equals to (y_j_t v y_j_t+1 ... v y_j_traceLength)                
        op = 'O' 
        once_rule = []
        if op in self.unaryOp:
            for i in range(2, self.d + 1):
                n_eval = []
                for j in range(1, i):
                    antecedent = self.l[i, j]
                    consequent = [] 
                    for t in range(trace.traceLength):
                        once_var = self.aux_once(sig, j, t)
    #                    logging.debug('%s <=> %s'%(sig[i,t], once_var))                   
                        consequent.append(EqualsOrIff(sig[i,t], once_var))
                    n_eval.append(Implies(antecedent, And(consequent)))
                    logging.debug('%s <=> Once(%s)'%(antecedent, consequent))                
                once_rule.append(Implies(self.x[i, op], And(n_eval)))
                
            logging.debug('Once Rule: %s'%(once_rule))
        
        #Historically
        logging.debug('[Sofar Rule] If a node i labeled with H and has a child j then sigma(i,t) is equal to  sigma_j_(0) & sigma_j_(1) & sigma_j_(2) & sigma_j_(t)')
        #Once rule
        #If a node i is labeled wit 'O'), then y_i_t is equals to (y_j_t v y_j_t+1 ... v y_j_traceLength)                
        op = 'H' 
        sofar_rule = []
        if op in self.unaryOp:
            for i in range(2, self.d + 1):
                n_eval = []
                for j in range(1, i):
                    antecedent = self.l[i, j]
                    consequent = [] 
                    for t in range(trace.traceLength):
                        sofar_var = self.aux_sofar(sig, j, t)
    #                    logging.debug('%s <=> %s'%(sig[i,t], sofar_var))                   
                        consequent.append(EqualsOrIff(sig[i,t], sofar_var))
                    n_eval.append(Implies(antecedent, And(consequent)))
                sofar_rule.append(Implies(self.x[i, op], And(n_eval)))
    
            logging.debug('Sofar Rule: %s'%(sofar_rule))

        #Historically
#        logging.debug('[Globally Rule] If a node i labeled with H and has a child j then sigma(i,t) is equal to  sigma_j_(0) & sigma_j_(1) & sigma_j_(2) & sigma_j_(t)')
        #Once rule
        #If a node i is labeled wit 'O'), then y_i_t is equals to (y_j_t v y_j_t+1 ... v y_j_traceLength)                
        op = 'G' 
        global_rule = []
        for i in range(2, self.d + 1):
            n_eval = []
            for j in range(1, i):
                antecedent = self.l[i, j]
                consequent = [] 
                for t in range(trace.traceLength):
                    g_var = self.aux_global(sig, j, t, trace.traceLength - 1)
                    consequent.append(EqualsOrIff(sig[i,t], g_var))
                n_eval.append(Implies(antecedent, And(consequent)))
            global_rule.append(Implies(self.x[i, op], And(n_eval)))
 
#        logging.debug('Globally Rule: %s'%(global_rule))
        
        #Globally???
        
        logging.debug('[Disjunction Rule] If a node i has a child j and j\' and labeled with | then sigma(i,t) is disjunction of sigma_j_t v sigma_j\'_t')            
        #Disjunction Rule        
        #If a node is labeled with '|', j is left child and j' is right child then (y_j_t or y_j'_t)
        op = '|'        
        disjunct_rule = []
        if op in self.binaryOp:
            for i in range(2, self.d + 1):
                for left in range(1, i):
                    or_eval = []
                    for right in range (1, i):
                        antecedent = And(self.l[i, left], self.r[i, right])
                        consequent = [] 
                        for t in range(trace.traceLength):
                            if left == right:
                                consequent.append(EqualsOrIff(sig[i,t], sig[left,t]))
                            else:
                                consequent.append(EqualsOrIff(sig[i,t], Or(sig[left,t], sig[right,t])))
    #                        print(antecedent, '=>',consequent)
                        or_eval.append(Implies(antecedent, And(consequent)))
                    disjunct_rule.append(Implies(self.x[i, op], And(or_eval)))                                     
            
            logging.debug('Disjunction Rule: %s'%(disjunct_rule))

        logging.debug('[Conjunctive Rule] If a node i has a child j and j\' and labeled with & then sigma(i,t) is disjunction of sigma_j_t & sigma_j\'_t')            
        #Disjunction Rule        
        #If a node is labeled with '|', j is left child and j' is right child then (y_j_t or y_j'_t)
        op = '&'        
        conjunct_rule = []
        if op in self.binaryOp:        
            for i in range(2, self.d + 1):
                for left in range(1, i):
                    and_eval = []
                    for right in range (1, i):
                        antecedent = And(self.l[i, left], self.r[i, right])
                        consequent = [] 
                        for t in range(trace.traceLength):
                            if left == right:
                                consequent.append(EqualsOrIff(sig[i,t], sig[left,t]))
                            else:
                                consequent.append(EqualsOrIff(sig[i,t], And(sig[left,t], sig[right,t])))
    #                        print(antecedent, '=>',consequent)
                        and_eval.append(Implies(antecedent, And(consequent)))
                    conjunct_rule.append(Implies(self.x[i, op], And(and_eval)))                                     
            
            logging.debug('Conjunctive Rule: %s'%(conjunct_rule))

        logging.debug('[Implication Rule] If a node i has a child j and j\' and labeled with => then sigma(i,t) is disjunction of sigma_j_t -> sigma_j\'_t')            
        #Disjunction Rule        
        #If a node is labeled with '|', j is left child and j' is right child then (y_j_t or y_j'_t)
        op = '=>'        
        implicate_rule = []
        if op in self.binaryOp:        
            for i in range(2, self.d + 1):
                for left in range(1, i):
                    or_eval = []
                    for right in range (1, i):
                        antecedent = And(self.l[i, left], self.r[i, right])
                        consequent = [] 
                        for t in range(trace.traceLength):
    #                        if left == right:
    #                            consequent.append(EqualsOrIff(sig[i,t], TRUE()))
    #                        else:
                            consequent.append(EqualsOrIff(sig[i,t], Or(Not(sig[left,t]), sig[right,t])))
                            if len(consequent) == 0:                                
                                print(antecedent, ' EMPTY =>',consequent)
                        or_eval.append(Implies(antecedent, And(consequent)))
                    if len(or_eval) == 0:                                
                        print(antecedent, ' EMPTY =>',consequent)
                        
                    implicate_rule.append(Implies(self.x[i, op], And(or_eval)))                                     
            
            logging.debug('Implication Rule: %s'%(implicate_rule))


        logging.debug('[Since Rule] If a node i has a child left and right and labeled with S then sigma(i,t) is sigma_left_0 v sigma_left_1 .. v sigma_left_t)')                    
        op = 'S'        
        since_rule = []
        if op in self.binaryOp:        
            for i in range(2, self.d + 1):
                for left in range(1, i):
                    and_eval = []
                    for right in range (1, i):
                        antecedent = And(self.l[i, left], self.r[i, right])
    #                    logging.debug('%s %s  %s'%(self.x[i, p], self.l[i, left], self.r[i, right]))
                        consequent = [] 
                        for t in range(trace.traceLength):
    #                        if left == right:
    #                            consequent.append(EqualsOrIff(sig[i,t], sig[left,t]))
    #                            logging.debug('%s <=> %s'%(sig[i,t], sig[left,t]))
    #                        else:                        
                            since_var = self.aux_since(sig, left, right, t)
    #                        print('Since Var Encodeing', since_var)                        
                            consequent.append(EqualsOrIff(sig[i,t], since_var))
    #                        logging.debug('%s <=> %s'%(sig[i,t], since_var))
                        and_eval.append(Implies(antecedent, And(consequent)))    
                    since_rule.append(Implies(self.x[i, op], And(and_eval)))
            logging.debug('Since Rule: %s'%(since_rule))
        
        logging.debug('Encoding trace semantics rules for trace %s'%(tId))
        
        trace_semantics = And(prop_rule) & And(neg_rule) & And(disjunct_rule) & And(conjunct_rule) & And(implicate_rule) & And(yesterday_rule) & And(once_rule) & And(sofar_rule) & And(since_rule) & And(global_rule)  
        
#        trace_cond = []
        
        if trace_type:
            #Accepting Trace 
#            trace_cond = []
#            for trace_index in range(trace.traceLength): 
#                trace_cond.append(sig[self.d, trace_index])
            
            accepted_cond = sig[self.d, 0]    
#            accept_trace.append(sig[2, 1])
             
#            trace_semantics = And(trace_semantics, Or(accepted_trace))
            trace_semantics = And(trace_semantics, accepted_cond)
            logging.debug('Accepting Trace %s'%(accepted_cond))
        else:
            #Rejecting Trace
#            for trace_index in range(trace.traceLength):
            #            print('>>>>>>>>>>>>', self.d)
#                trace_cond.append(Not(sig[self.d, trace_index]))
#            reject_trace = Not(sig[2, 0])
            rejected_cond = Not(sig[self.d, 0]) 
            
            trace_semantics = And(trace_semantics,  rejected_cond) 
            logging.debug('Rejecting Trace %s'%(rejected_cond)) 
        
        return trace_semantics


                    
    def aux_since(self, sig, left, right, t):
        if t > 0:
            return Or(sig[right,t], And(sig[left,t], self.aux_since(sig, left, right, t-1)))
        else:
            return sig[right,t]              

    def aux_once(self, sig, left, t):
        if t > 0:
            o_var = Or(sig[left,t], self.aux_once(sig, left, t-1))
            return o_var
        return sig[left,t]

    def aux_sofar(self, sig, left, t):
        if t > 0:
            h_var = And(sig[left,t], self.aux_sofar(sig, left, t-1))
            return h_var
        return sig[left,t]

    def aux_global(self, sig, left, t, bound):
        if t < bound:
            h_var = And(sig[left,t], self.aux_global(sig, left, t+1, bound))
            return h_var
        return sig[left, t]

    def aux_yesterday(self, sig, left, t):
        if t > 0:
            y_var = sig[left, t-1]
            return y_var
        else:
#            y_var = And(Not(sig[left, t]), sig[left, t])
#            y_var = Not(sig[left, t]) 
            y_var = FALSE()
        return y_var
                     
    def m2f(self, size , model):
        
        def truth_value(depth, variables):
            for v in variables:                
                vflag = model[variables[v]]
                if(v[0] == depth and vflag.is_true()):
#                    logging.debug('%s := %s'%(str(v[0]), str(vflag)))
                    return v[1]
                                                       
        #Can filter SAT variables?            
        label = truth_value(size, self.x)
#        print('label', label)
#        print('Depth', depth)            
        if(label in self.Constants):
            if label == 'Top':
                label = 'TRUE'
            else:
                label = 'FALSE'    
            f = PLTLFormula([label, None, None])
#            print('Formula', f)
            return f

        if(label in self.AP):
            f = PLTLFormula([str(label), None, None])
#            print('Formula', f)
            return f
        elif(label in self.unaryOp):
            left = truth_value(size, self.l)
            f =  PLTLFormula([label, self.m2f(left, model)])
#            print('Formula',f)
            return f
        elif(label in self.binaryOp):
            left = truth_value(size, self.l)
            right = truth_value(size, self.r)                
            f = PLTLFormula([label, self.m2f(left, model), self.m2f(right, model)])
#            print('Formula',f)
            return f

    def dag_shape(self, model):
        partial_model = []
        
        for (label, value) in model:
            if value.is_false():
                continue
            else:
                s = label.symbol_name()
#                print(s)
                #Type x, l or r
                if(s[0] == 'x'):
#                    print('VALUE+++++++',s)
                    partial_model.append(EqualsOrIff(label, value))
                    
                if(s[0] == 'l'):
#                    print('LEFT+++++++',s)
                    partial_model.append(EqualsOrIff(label, value))                    
#                    partial_model.append(EqualsOrIff(label, value))
                if(s[0] == 'r'):
#                    print('RIGHT+++++++',s)
                    partial_model.append(EqualsOrIff(label, value))                    
#                    partial_model.append(EqualsOrIff(label, value))                    
#                    print(s,'vertex', s[2], s[4:])
                    
#                else:
#                    print(s,s[0], 'edge', s[2], s[4])
    
        return partial_model
    
    def tmp_data(self):
        clauses = []
        
        clauses.append(self.x[1,'p'])
        clauses.append(self.x[2,'q'])
        clauses.append(self.l[4,3])
        
        return And(clauses)    
                            
if __name__ == '__main__':
    
    logging.basicConfig(level=logging.DEBUG)

#    trace = Trace("1,1;1,1")
#    trace = Trace("1,1;0,0;0,0;0,0;1,1;1,0;1,0", 'A')

    trace = Trace("1,1,0;0,0,0", 'A')
    
    
    
    unary_operators = ['!', 'Y', 'O', 'H']
    binary_operators = ['S','&', '|', '=>']
    
    AP_Lit = None
    
    sat_en = SATEncoder(2, trace.vars,unary_operators, binary_operators, AP_Lit)
    shape_fml = sat_en.encode_shape()
    
    benign_fml_enc = []

    _enc_fml = sat_en.encode_trace(trace, True)
    benign_fml_enc.append(_enc_fml)

    _fml_enc = shape_fml & And(benign_fml_enc) #& And(rejected_fml_enc) 
    

    #Remove depreciated class problem.
    logging.debug('size %d'%(get_formula_size(_fml_enc)))
    
    sat_solver = SATSolver('z3')

    sat_solver.assert_cls(_fml_enc)
    
    model = sat_solver.get_model()
    fail_safe = 0;
    
    while model is not None:
        
        pLTL_fml = sat_en.m2f(2, model)
        pmodel = sat_en.dag_shape(model)
        model = sat_solver.enum_model(pmodel)    
        
#        logging.debug('Generated PLTL Formula: %s'%(pLTL_fml))

        if pLTL_fml:
            sat = trace.check_truth(pLTL_fml)
        
        print(pLTL_fml)
#        break
#            if(sat):
#                logging.debug('%d - %s over trace %s is SAT'%(fail_safe, pLTL_fml, trace.Id))
#            else:
#                logging.debug('%d - %s over trace %s is UNSAT'%(fail_safe, pLTL_fml, trace.Id))    
#                break;
#        
#        if fail_safe > 2000:
#            break;
#        fail_safe += 1    
#    else:        
#        logging.warning('No Model Found!')
        
#        sat_solver.unsat_core()        