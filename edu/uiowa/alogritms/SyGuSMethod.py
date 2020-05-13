from edu.uiowa.encoder.SyGuSEncoder import ADTEncoder, BVEncoder
from edu.uiowa.parser.LarkParser import pLTLParser
from edu.uiowa.utils.RunCmd import run_sygus
from edu.uiowa.utils.Printer import eval_result
import timeit
import logging

        
def run_adt_sygus_algo(_ADT_Def_file, _size, _count, trace_file, benign_traces, rejected_traces, unary_ops =  ['!', 'Y', 'O', 'H'], binary_ops = ['S','&', '|', '=>'], AP_Lit = None): 

    start_time = timeit.default_timer()

    traces = benign_traces + rejected_traces
    
    nvars = benign_traces[0].vars

    _syngus = ADTEncoder(nvars, traces, len(benign_traces), len(traces))

    _adt_def = _ADT_Def_file.read() 
    
    _adt_def = _syngus.sygus_adt_def(_adt_def)
    
    if AP_Lit:
        key_vars = []
        for n in range(nvars):
            key = 'p' + str(n)
            key_vars.append(key)

            vars_dict = dict(zip(key_vars, list(AP_Lit)))

    
    tmp_result = run_sygus(_adt_def, start_time, trace_file, _count, False)

    parser = pLTLParser()
    result = []
    
    for f in tmp_result:
        if AP_Lit:
            f = parser.dict_var(f, vars_dict)                
        result.append(f)

    logging.debug('Checking Synthesize pLTL Formulae...')
    eval_result(result, benign_traces, rejected_traces, _count)
    logging.debug('Synthesized Signatures: %s'%(result))
    
    
    return result



def run_bv_sygus_algo(_BV_Def_file, _size, _count, trace_file, benign_traces, rejected_traces, unary_ops =  ['!', 'Y', 'O', 'H'], binary_ops = ['S','&', '|', '=>'], max_trace_length = 0, AP_Lit = None): 

    start_time = timeit.default_timer()
        
    nvars = benign_traces[0].vars
    
    if AP_Lit is None:
        AP_Lit = []
        for n in range(nvars):
            key = 'p' + str(n)
            AP_Lit.append(key)

    _syngus = BVEncoder(nvars, benign_traces, rejected_traces, max_trace_length, AP_Lit)
    
    _bv_def = _BV_Def_file.read() 
    
    _bv_def = _syngus.bv_sygus_latest_def(_bv_def)
    
    result = run_sygus(_bv_def, start_time, trace_file, _count)

    stop = timeit.default_timer()
    elasped_time = ('%.2f')%(stop - start_time)
    
    logging.info('Total Running Time Time: %s seconds'%(elasped_time))

    logging.debug('Checking Synthesize pLTL Formulae...')

    eval_result(result, benign_traces, rejected_traces, _count)

    logging.debug('Synthesized Signatures: %s'%(result))
    
    
    return result


