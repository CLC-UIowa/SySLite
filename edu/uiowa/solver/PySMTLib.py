from pysmt.shortcuts import Solver, EqualsOrIff, Not, And
from pysmt.oracles import get_logic
 

class PySMT:
    
    def get_models(self, fml, blocking, count):
        t_logic = get_logic(fml)
        models = []
        m_index = 0
        
        with Solver(logic = t_logic) as solver:
            solver.add_assertion(fml)
            while (solver.solve()):
                partial_model = [EqualsOrIff(b, solver.get_value(b)) for b in blocking]
                m = solver.get_model()

                models.append(m)
                solver.add_assertion(Not(And(partial_model)))
                m_index += 1  
                if m_index > count:
                    break
        return models      

    def dag_shape(self, model):
        
        for (label, value) in model:
            if value.is_false():
                continue
            else:
                s = label.symbol_name()
                #Type x, l or r
                if(s[0] == 'x'):
                    print('vertex', s[2], s[4:])
                else:
                    print(s[0], 'edge', s[2], s[4])
                    
