#!/usr/bin/env python3
# encoding: utf-8
'''
SySLite -- A past-time LTL synthesis program that support a number of
decision procedures (i.e. SAT/SMT/SyGuS based) to learn formulas from a
given set of finite traces.

@author:     mfarif

@copyright:  2020 The University of Iowa. All rights reserved.

@license:    license

@contact:    muhammad-arif@uiowa.edu
'''
      
from edu.uiowa.synz.pLTLSynthesizer import synthesize_pLTL
from edu.uiowa.utils.CmdLine import cmd_parser, parse_sig_options
from edu.uiowa.utils.FileReader import read_traces_1
from edu.uiowa.utils.Printer import eval_result

import timeit
import logging


def setup_logging(logging_level):

    
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    
    logger.handlers = [] 
    
    # Start defining and assigning your handlers here
    handler = logging.StreamHandler()
    handler.setLevel(logging_level)
    formatter = logging.Formatter("%(asctime)s: %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    
if __name__ == "__main__":
    
    setup_logging(logging.INFO)    
        
    start = timeit.default_timer()
        
    args = cmd_parser()
    
    #Synthesize Signature
    _size, _count, trace_file, _algo_type, _dict_support, result_file, solver_type = parse_sig_options(args)
        
    if not trace_file:
        print('No Input Trace File Provided!')
        quit()
    
    if _dict_support:
        print('Dictionary Support Enabled')
    else:
        print('Dictionary Support Disabled')

    AP_Lit, benign_traces, rejected_traces, unary_operators, binary_operators, _nsize, target_fml, max_trace_length = read_traces_1(trace_file, _dict_support)
    
    synthesize_pLTL(_size, _count, AP_Lit, _algo_type, solver_type, result_file, trace_file, benign_traces, rejected_traces, unary_operators, binary_operators, _nsize, target_fml, max_trace_length)
            
    
    stop = timeit.default_timer()
    elasped_time = ('%.2f')%(stop - start)
    logging.info('Time: %s seconds'%(elasped_time))
    