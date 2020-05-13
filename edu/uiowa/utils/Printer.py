'''
@author: marif
'''

import logging

#print the results
def eval_result(_result, benign_traces, rejected_traces, _count):        
    
    fail_safe = 1
    _suspected_result = dict()

        
    for pLTL_fml in _result:

        for trace in benign_traces:
            
            sat = trace.check_truth(pLTL_fml)
            
            if(sat):
                logging.debug('%d - %s over trace %s is SAT'%(fail_safe, pLTL_fml, trace.Id ))                
            else:
                logging.debug('%d - %s over trace %s is UNSAT'%(fail_safe, pLTL_fml, trace.Id))
                _suspected_result[fail_safe] = (pLTL_fml, trace.Id)

        for trace in rejected_traces:

            sat = trace.check_truth(pLTL_fml)

            if( not sat):
                logging.debug('%d - %s over trace %s is UNSAT'%(fail_safe, pLTL_fml, trace.Id ))                
            else:
                logging.debug('%d - %s over trace %s is SAT'%(fail_safe, pLTL_fml, trace.Id ))                
                _suspected_result[fail_safe] = (pLTL_fml, trace.Id)
                            
            for trace_index in range(trace.traceLength): 
                sat = trace.truthValue(pLTL_fml, trace_index)
                
                if(sat):
                    logging.debug('%s over trace %s is SAT @index(%d)'%(pLTL_fml, trace.Id, trace_index))
                else:
                    logging.debug('%s over trace %s is UNSAT @index(%d)'%(pLTL_fml, trace.Id, trace_index))    
                    
    else:        
        logging.debug('Finished Searching Models!')
    
    cCheck = True        

    for key in _suspected_result.keys():
        fml, traceId = _suspected_result[key]
        logging.warn('(%s) %s fails for Trace %s'%(key,fml, traceId))
        cCheck = False
        
    return cCheck

