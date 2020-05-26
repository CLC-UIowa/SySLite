#!/usr/bin/env python3
# encoding: utf-8
'''
@Program: SySLite is past-time LTL synthesis program that use various
decision procedures (i.e. SAT/SMT/SyGuS-based) to learn formulas from a
given set finite traces.

@Copyright (c) 2020, Board of Trustees of the University of Iowa. All rights reserved.

@License: Use of this source code is governed by a BSD 3-Clause License that can be found in the LICENSE file.

@Contact: fareed.arif@yahoo.com
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
    