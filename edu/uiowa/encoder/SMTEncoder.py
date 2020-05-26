'''
Copyright (c) 2020, Board of Trustees of the University of Iowa.
All rights reserved.

Use of this source code is governed by a BSD 3-Clause License that
can be found in the LICENSE file.
'''

from edu.uiowa.encoder.SyGuSEncoder import trace_vars, trace_len, enum_trace, pos_length_def

class SMTEncoder:
    
    def __init__(self, nvars, traces, b_traces_bound, r_traces_bound):
        self.nvars = nvars
        self.traces = traces
        self.b_traces_bound = b_traces_bound
        self.r_traces_bound = r_traces_bound
              
    def smt_adt_def(self, adt_def):
        
        
#        adt_def = adt_file.read()   
        
        #Variables 
        adt_def = adt_def.replace(';%{0}', trace_vars(self.nvars))    
           
        #Trace Length 
        adt_def = adt_def.replace(';%{1}', trace_len(self.traces))        
            
        #Trace Values
        adt_def = adt_def.replace(';%{2}', enum_trace(self.traces))
            
        #Length of Positive Trace
        adt_def = adt_def.replace(';%{3}', pos_length_def(self.b_traces_bound))
    
        #Length of Negative Traces
        adt_def = adt_def.replace(';%{4}', neg_traces_assert(self.r_traces_bound))
            
        return adt_def 

def neg_traces_assert(neg_len):
    const_def = '(assert (fail-for-all-traces %d phi))\n'%(neg_len)
    return const_def    
