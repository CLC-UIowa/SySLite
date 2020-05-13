'''
@author: marif
'''
from edu.uiowa.parser.Tracer import Trace
from edu.uiowa.parser.LarkParser import pLTLParser

#Enumeration Constructs
AP_Lit, POS_TRACE, NEG_TRACE, UNARY_OP, BINARY_OP, SIZE, TARGET_FML, = range(1, 8)

#Adopt the trace format suggested by Daniel Neider & Garvan.

#Read alphabet and example traces from the provided file
def read_traces(fp):
    
    benign_traces = []
    rejected_traces = []

    _flg = True
    
    line = fp.readline()
    cnt = 0    

    while line:
        cnt += 1

        data = line.strip()

        if data == '---':                
            _flg = False
            line = fp.readline()
            
            continue

        trace = Trace(data, str(cnt))
        
        
        if _flg:
            benign_traces.append(trace)
        else:    
            rejected_traces.append(trace)
        
        line = fp.readline()
        
    return (benign_traces, rejected_traces)

#Read alphabet and example traces from the provided file
def read_traces_1(fp, isLit = False):
    
    benign_traces = []
    
    rejected_traces = []
    
    op1 = []
    op2 = []
    
    size = -1
    
    max_trace_length = 0 

    if isLit:
        trace_type = AP_Lit
    else:
        trace_type = POS_TRACE

    line = fp.readline()
    cnt = 0    
    
    AP = None
    
    while line:
        
        cnt += 1
        data = line.strip()

        if data == '---':                
            trace_type = next_type(trace_type)
            line = fp.readline()            
            continue

        fml = None

        if trace_type is AP_Lit:
            AP = list(data.split(","))
        elif trace_type is POS_TRACE:
            if isLit:
                ptrace = Trace(data, str(cnt), AP)                
            else:
                ptrace = Trace(data, str(cnt))    
                
            benign_traces.append(ptrace)
            if max_trace_length < ptrace.traceLength:
                max_trace_length =  ptrace.traceLength

        elif trace_type is NEG_TRACE:
            if isLit:
                ntrace = Trace(data, str(cnt), AP)
            else:
                ntrace = Trace(data, str(cnt))        
            rejected_traces.append(ntrace)
            
            if max_trace_length < ntrace.traceLength:
                max_trace_length =  ntrace.traceLength
            
        elif trace_type is UNARY_OP:    
            op1 = data.split(",") 

        elif trace_type is BINARY_OP:    
            op2 = data.split(",")

        elif trace_type is SIZE:    
            size = int(data)

        elif trace_type is TARGET_FML:   
            target = data

            if not target is None: 
                parser = pLTLParser()
                fml = parser.parse(target)
                
        line = fp.readline()

    return (AP, benign_traces, rejected_traces, op1, op2, size, fml, max_trace_length)

#Read alphabet and example traces from the provided file
def read_traces_2(fp, isLit = False):
    
    benign_traces = []
    
    rejected_traces = []
    
    if isLit:
        trace_type = AP_Lit
    else:
        trace_type = POS_TRACE

    line = fp.readline()
    cnt = 0    
    
    AP = None
    
    while line:
        
        cnt += 1
        data = line.strip()

        if data == '---':                
            trace_type = next_type(trace_type)
            line = fp.readline()            
            continue

        if trace_type is AP_Lit:
            AP = list(data.split(","))            
        
        elif trace_type is POS_TRACE:
            benign_traces.append(data)

        elif trace_type is NEG_TRACE:
            rejected_traces.append(data)

        line = fp.readline()

    return (AP, benign_traces, rejected_traces)

#mode function
def next_type(trace_type):
    
    
    if trace_type is AP_Lit:
#        print('APT --> POS')
        return POS_TRACE
    elif trace_type is POS_TRACE:
#        print('POS --> NEG')
        return NEG_TRACE
    elif trace_type is NEG_TRACE:
#        print('NEG --> Unary')
        return UNARY_OP   
    elif trace_type is UNARY_OP:
#        print('Unary --> Binary')
        return BINARY_OP
    elif trace_type is BINARY_OP:
#        print('Binary -- > SIZE ')
        return SIZE
    elif trace_type is SIZE:
#        print('Binary -- > TARGET FML ')        
        return TARGET_FML
    
def max_trace_size(benign_traces, rejected_traces):
    max_trace_length = 0
    
    for tr in benign_traces:
        if max_trace_length < tr.traceLength:
            max_trace_length = tr.traceLength

    for tr in rejected_traces:
        if max_trace_length < tr.traceLength:
            max_trace_length = tr.traceLength
    return max_trace_length
    
