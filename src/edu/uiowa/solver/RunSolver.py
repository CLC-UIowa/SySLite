'''
Copyright (c) 2020, Board of Trustees of the University of Iowa.
All rights reserved.

Use of this source code is governed by a BSD 3-Clause License that
can be found in the LICENSE file.
'''

from pysmt.shortcuts import And, Not, Solver, get_unsat_core
from pysmt.logics import QF_BOOL 
from pysmt.rewritings import conjunctive_partition  

class SATSolver:
     
    def __init__(self, solver_name):         
        self.solver = Solver(solver_name, logic = QF_BOOL)
           
    def get_model(self):
        m = None        
        res = self.solver.solve()
        if res:
            m = self.solver.get_model()
        return m
                 
    def enum_model(self, blocking_cls):
        m = None
        self.solver.add_assertion(Not(And(blocking_cls)))
        res = self.solver.solve()
        if res:
            m = self.solver.get_model()
        return m      

    def assert_cls(self, _cls):
        self.solver.add_assertion(_cls)

    def add_cls(self, _cls, level):
        self.solver.push(level)
        self.solver.add_assertion(_cls)
        
    def remove_cls(self, level):
        self.solver.pop(level)

    def unsat_core(self):
        
        res = self.solver.solve()
        
        if not res:
            print('Assertions:', self.fml)            
            conj = conjunctive_partition(self.fml)
            ucore = get_unsat_core(conj)
            print("UNSAT-Core size '%d'" % len(ucore))
        for f in ucore:
            print(f.serialize())
            
    def clear_solver(self):        
        self.solver.exit() 
#        print("Clearing and closing the solver")       