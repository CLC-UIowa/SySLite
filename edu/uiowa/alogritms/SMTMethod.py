from edu.uiowa.encoder.SMTEncoder import SMTEncoder
from edu.uiowa.parser.LarkParser import pLTLParser
from edu.uiowa.utils.RunCmd import run_smt2
from edu.uiowa.utils.Printer import eval_result
from edu.uiowa.utils.FileReader import max_trace_size

import timeit
import logging


def run_adt_fin_algo(_ADT_Def_file, _size, _count, trace_file, benign_traces, rejected_traces, unary_ops =  ['!', 'Y', 'O', 'H'], binary_ops = ['S','&', '|', '=>'], AP_Lit = None): 

    start_time = timeit.default_timer()


    traces = benign_traces + rejected_traces

    nvars = max_trace_size(benign_traces, rejected_traces)

    _adtencoder = SMTEncoder(nvars, traces, len(benign_traces), len(traces))

    _adt_def = _ADT_Def_file.read() 
    
    _adt_def = _adtencoder.smt_adt_def(_adt_def)
    

    if AP_Lit:
        key_vars = []
        for n in range(nvars):
            key = 'p' + str(n)
            key_vars.append(key)

            vars_dict = dict(zip(key_vars, list(AP_Lit)))

    
    tmp_result = run_smt2(_adt_def, start_time, trace_file, _count)
        
    cnt = 0    
    result = []
     
    for f in tmp_result:
        cnt += 1

        if f:
            if AP_Lit:
                f = parser.rename_var(f, vars_dict)                
            result.append(f)
            print('(%d) %s '%(cnt, f))
            
        line = fp.readline()

    logging.debug('Checking Synthesize pLTL Formulae...')

    eval_result(result, benign_traces, rejected_traces, _count)
    
    logging.debug('Synthesized Signatures: %s'%(result))
    
    
    return result
