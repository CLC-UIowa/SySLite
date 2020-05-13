'''
Created on Dec 30, 2019

@author: marif
'''

class ADTEncoder:
    
#    def __init__(self, size, nr_vars, unary_operators, binary_operators, AP_Lit):
#        self.vars = 
    
    def __init__(self, nvars, traces, b_traces_bound, r_traces_bound):
        self.nvars = nvars
        self.traces = traces
        self.b_traces_bound = b_traces_bound
        self.r_traces_bound = r_traces_bound
              
    def sygus_adt_def(self, adt_def):
        
        
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
        adt_def = adt_def.replace(';%{4}', fail_constraint(self.r_traces_bound))
            
        return adt_def 
    

def trace_vars(nvars):

    _sygus_var = []    
         
    for v in range(nvars):       
        _sygus_var.append(str(v))
    _sygus_var = ' '.join(_sygus_var)
    
    _sygus_var_def = '(<I> Int (%s))'%(_sygus_var)    
           
    
    return _sygus_var_def


def pos_length_def(pos_len):
    pos_len_def = '(define-const pos_tr Int %d)\n'%(pos_len)
    
    return pos_len_def
                 
def trace_len(traces):
    def_ite = ite(traces, 1, len(traces))
    
    def_tr_len = '(define-fun len ((tr Trace)) Int %s\n)'%(def_ite)

    return def_tr_len
          
def ite(traces, index, _count):
    #trace ID + length.
    if index > _count:
        return '0'
        
    trace = traces[index - 1]
    
    return '\n    (ite %s %s)'%(_len(trace, index), ite(traces, index+1, _count))
    
def _len(trace, index):
    
    if index < 0:
        return 
    else:        
        return '(= tr %d) %d'%(index,trace.traceLength - 1)                         

#Trace(traceId, time)
def enum_trace(traces):
    traces_def = []
    traceId = 1
    for trace in traces:
        t_def = trace_data(traceId, 0, trace.traceVector, [])
        traces_def.append(t_def)
        traceId += 1
#        print(tr_def)
    traces_def = '\n'.join(traces_def)
    return "(define-fun val ((tr Trace) (t Time) (x VarId)) Bool\n    (or \n%s)\n)"%(traces_def)

        
def trace_data(t_Id, t_index, traceVector,  trace_def):
        
    if t_index > len(traceVector) - 1:
        return 
    
    trace_values = traceVector[t_index]
    
#    print('********',trace_values)
    v_index = 0
    for v in trace_values:
        if v is True:
            trace_def.append('    (and (= tr %s) (= t %d) (= x %d))'%(t_Id, t_index, v_index))        
        v_index += 1
    trace_data(t_Id, t_index + 1, traceVector, trace_def)

    return '\n'.join(trace_def)        
    

def fail_constraint(neg_len):
    const_def = '(constraint (fail-for-all-traces %d phi))\n'%(neg_len)
    return const_def


class BVEncoder:

    def __init__(self, nvars, pos_traces, neg_traces, max_trace_length, AP_Lit):
        self.nvars = nvars
        self.pos_traces = pos_traces
        self.neg_traces = neg_traces
        self.vars = max_trace_length
#        self.max_trace_length = 
        
        self.AP = list(AP_Lit)
    
    def bv_fixed_sygus_def(self, bv_def):
    
        #Variables 
#        print('0000000000000000000000000000000*********', self.vars)
        bv_def = bv_def.replace(';%{1}', define_streams(self.vars))    

        #Variables in SyGus Grammar
        bv_def = bv_def.replace(';%{2}', define_vars_stream(self.AP))
        
        #Trace Length 
#        bv_def = bv_def.replace(';%{3}', define_vars_stream(self.nvars, self.AP))        
           
        #Trace Length 
        bv_def = bv_def.replace(';%{3}', define_vars(self.nvars, self.AP))        
            
        #Trace Values
        bv_def = bv_def.replace(';%{4}', enum_fixed_traces(self.pos_traces, self.nvars, True))
             
        #Length of Positive Trace
        bv_def = bv_def.replace(';%{5}', enum_fixed_traces(self.neg_traces, self.nvars, False))
        
        return bv_def 

    def bv_sygus_def(self, bv_def):
    
        #Variables 
#        print('0000000000000000000000000000000*********', self.vars)
        bv_def = bv_def.replace(';%{1}', define_streams(self.vars))    

        #Variables in SyGus Grammar
        bv_def = bv_def.replace(';%{2}', define_vars_stream(self.AP))
        
        #Trace Length 
#        bv_def = bv_def.replace(';%{3}', define_vars_stream(self.nvars, self.AP))        
           
        #Trace Length 
        bv_def = bv_def.replace(';%{3}', define_vars(self.nvars, self.AP))        
            
        #Trace Values
        bv_def = bv_def.replace(';%{4}', enum_traces(self.pos_traces, self.nvars, True, self.vars))
             
        #Length of Positive Trace
        bv_def = bv_def.replace(';%{5}', enum_traces(self.neg_traces, self.nvars, False, self.vars))
        
        return bv_def 
    

    def bv_sygus_latest_def(self, bv_def):
    
        #Variables 
#        print('0000000000000000000000000000000*********', self.vars)
        bv_def = bv_def.replace(';%{1}', define_streams(self.vars))    

        #Variables in SyGus Grammar
        bv_def = bv_def.replace(';%{2}', define_vars_stream(self.AP))
        
        #Trace Length 
#        bv_def = bv_def.replace(';%{3}', define_vars_stream(self.nvars, self.AP))        
           
#        #Trace Length 
#        bv_def = bv_def.replace(';%{3}', define_vars(self.nvars, self.AP))        
            
        #Trace Values
        bv_def = bv_def.replace(';%{3}', enum_traces(self.pos_traces, self.nvars, True, self.vars))
             
        #Length of Positive Trace
        if len(self.neg_traces) > 0:
            bv_def = bv_def.replace(';%{4}', enum_traces(self.neg_traces, self.nvars, False, self.vars))
        
        return bv_def 
    
    def bv_sygus_non_recur_def(self, bv_def):
    
        #Variables 
        bv_def = bv_def.replace(';%{1}', define_streams(self.vars))    

        #Since Operator
        bv_def = bv_def.replace(';%{2}', define_since_op(self.vars))        

        #Variables in SyGus Grammar
        bv_def = bv_def.replace(';%{3}', define_vars_stream(self.AP))        
           
        #Variables
        bv_def = bv_def.replace(';%{4}', define_vars(self.nvars, self.AP))        
            
        #Trace Values
        bv_def = bv_def.replace(';%{5}', enum_traces(self.pos_traces, self.nvars, True, self.vars))
             
        #Length of Positive Trace
        bv_def = bv_def.replace(';%{6}', enum_traces(self.neg_traces, self.nvars, False, self.vars))
        
        return bv_def 

    def bv_fixed_sygus_non_recur_def(self, bv_def):
    
        #Variables 
        bv_def = bv_def.replace(';%{1}', define_streams(self.vars))    

        #Since Operator
        bv_def = bv_def.replace(';%{2}', define_since_op(self.vars))        

        #Variables in SyGus Grammar
        bv_def = bv_def.replace(';%{3}', define_vars_stream(self.AP))        
           
        #Variables
        bv_def = bv_def.replace(';%{4}', define_vars(self.nvars, self.AP))        
            
        #Trace Values
        bv_def = bv_def.replace(';%{5}', enum_fixed_traces(self.pos_traces, self.nvars, True))
             
        #Length of Positive Trace
        bv_def = bv_def.replace(';%{6}', enum_fixed_traces(self.neg_traces, self.nvars, False))
        
        return bv_def 
    
    
#def define_bv_size(vars):
#    _bv_size_const = '(define-const BV_SIZE Int %d)\n'%(vars)    
#    return _bv_size_const
 
def define_since_op(nvars):
    var_1 = '(ite (TrueAt (_ bv0 %d) Z) (Ht (_ bv1 %d) X) ZERO)\n'%(nvars, nvars)
    var_2 = '        (ite (TrueAt (_ bv1 %d) Z) (Ht (_ bv2 %d) X) ZERO)\n'%(nvars, nvars)
    _since_def = var_1 + var_2
    return _since_def

def define_vars_stream(AP=[]):
    
    stream_vars = []
    for v in AP:
        v_stream = '(%s Stream)'%(v)
        stream_vars.append(v_stream)
    vars_stream = ' '.join(stream_vars)
    
    return vars_stream 

def define_streams(nvars):
    
    _stream = '(define-sort Stream () (_ BitVec %d))\n'%(nvars)
    
    _zero_stream = '(define-fun ZERO () Stream (_ bv0 %d))\n'%(nvars)
    _one_stream = '(define-fun ONE () Stream (_ bv1 %d))\n'%(nvars)

    _stream_def = ''.join(_stream  +_zero_stream+_one_stream)       
    
    return _stream_def


def define_vars(nvars, AP=[]):

    _sygus_var = []    

    if len(AP) == 0:
        _vars = []
        for n in range(nvars):
            v = 'p' + str(n)
            _vars.append(v)
        
        AP = _vars
                                 
    for v in AP:       
        _sygus_var.append(v)
        
    _sygus_var = '\n     '.join(_sygus_var)
                   
    return _sygus_var


def enum_fixed_traces(_traces, nvars, _type):
    _trace_data = []
    
    
    for tr in _traces:
        trace_value = tr.traceVector[::-1]
        trace_value = trace_bv_fixed_data(trace_value, nvars)
        if _type:
            _value = '    (= (phi %s) S_TRUE)'%(trace_value)
        else:
            _value = '    (not (= (phi %s) S_TRUE))'%(trace_value)     
        _trace_data.append(_value)
    v = '\n'.join(_trace_data)
       
    _trace_data = '(constraint\n   (and\n%s \n   )\n)'%(v)
#    print(_trace_data)
            
    return _trace_data

def trace_bv_fixed_data(traces, nvars):
    #while v_index < nvars:
    trace_value  = []
    v_index = 0
#    (= (phi
    while v_index < nvars:
        var_value = []
        for vector in  traces:
            if vector[v_index]:
                var_value.append('1')
            else:
                var_value.append('0')                    
#            var_value.append(vector[v_index])
        v = ''.join(var_value)
        trace_value.append('#b%s'%(v))
            
#        print('#b%s'%(v))                
        v_index += 1
#    print(trace_value)    
    return ' '.join(trace_value)       


def enum_traces(_traces, nvars, _type, max_vars):
    _trace_data = []
    
    
    for tr in _traces:
#        print('*******Trace ID', tr.Id)
        trace_value = tr.traceVector[::-1]
#        print('*******(inverted)', trace_value)
#        print('*******(nvars)', nvars)
#        print('*******(max_vars)', max_vars)
        trace_value = trace_bv_data(trace_value, nvars, max_vars)
#(= ((_ extract 1 0) (phi #b000 #b000)) ((_ extract 1 0) S_TRUE))                
        if _type:
            trace_len = tr.traceLength
            if trace_len < max_vars:
                _value = '    (= ((_ extract %d 0) (phi %s)) ((_ extract %d 0) S_TRUE))'%(trace_len - 1, trace_value, trace_len - 1)
            else:
                _value = '    (= (phi %s) S_TRUE)'%(trace_value)     
#            _value = '    (= (phi %s) S_TRUE)'%(trace_value)
        else:
            trace_len = tr.traceLength
            if trace_len < max_vars:            
                _value = '    (not (= ((_ extract %d 0) (phi %s)) ((_ extract %d 0) S_TRUE)))'%(trace_len - 1,trace_value, trace_len - 1)            
            else:
                _value = '    (not (= (phi %s) S_TRUE))'%(trace_value)
#            _value = '    (not (= (phi %s) S_TRUE))'%(trace_value)     
        _trace_data.append(_value)
    v = '\n'.join(_trace_data)
       
    _trace_data = '(constraint\n   (and\n%s \n   )\n)'%(v)
#    print(_trace_data)
            
    return _trace_data
        
def trace_bv_data(traces, nvars, max_length):
    #while v_index < nvars:
    trace_value  = []
    v_index = 0
#    (= (phi
    
    while v_index < nvars:
        var_value = []
        
        for vector in  traces:
#            print('******Vector Length', len(vector), ' index: ', v_index )
            if vector[v_index]:
                var_value.append('1')
            else:
                var_value.append('0')                    
#            var_value.append(vector[v_index])
        values_length = len(var_value)
        
        pad = '0'* (max_length - values_length)                    
            
        v = ''.join(var_value)
        
        if values_length < max_length:
            v = pad + v
        trace_value.append('#b%s'%(v))
            
#        print('#b%s'%(v))                
        v_index += 1
#    print(trace_value)    
    return ' '.join(trace_value)       
