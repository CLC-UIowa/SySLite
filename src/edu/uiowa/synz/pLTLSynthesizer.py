'''
Copyright (c) 2020, Board of Trustees of the University of Iowa.
All rights reserved.

Use of this source code is governed by a BSD 3-Clause License that
can be found in the LICENSE file.
'''

from edu.uiowa.alogritms.SATMethod import run_sat_algo, run_enum_sat_algo, run_guided_sat_algo, run_guided_sat_enum_algo
#from edu.uiowa.alogritms.DecisionTreeMethod import run_dt_algo, run_scikit_dt_algo
from edu.uiowa.alogritms.SyGuSMethod import run_adt_sygus_algo, run_bv_sygus_algo
from edu.uiowa.alogritms.SMTMethod import run_adt_fin_algo

from edu.uiowa.utils.FileReader import read_traces_1

import os
import logging


def synthesize_pLTL(_size, _count, AP_Lit, _algo_type, solver_type, result_file, trace_file, benign_traces, rejected_traces, unary_operators, binary_operators, _nsize, target_fml, max_trace_length):
    
    if len(unary_operators) == 0 and  len(binary_operators) == 0:
        
        unary_operators =  ['!', 'Y', 'O', 'H', 'G']
        binary_operators = ['S','&', '|', '=>']

    logging.info('*** AP:%s'%(AP_Lit))
#    for trace in benign_traces:
    logging.info('*** +ve Traces Size:%d'%(len(benign_traces)))
#    for trace in rejected_traces:    
    logging.info('*** -ve Traces Size:%d'%(len(rejected_traces)))
    logging.debug('*** Unary Operators:%s'%(unary_operators))
    logging.debug('*** Binary Operators:%s'%(binary_operators))
    logging.info('*** Formula Size:%d'%(_size))
    
    logging.debug(target_fml)
    
    
    _result = []
    
    #SAT Algorithm.
    if _algo_type == 'sat' :
        logging.info('*** Selected Solver:%s'%(solver_type))
        _result = run_sat_algo(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit, solver_type)    
    
    elif _algo_type == 'sat_enum' :
        _result = run_enum_sat_algo(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit, solver_type)    

    elif _algo_type == 'guided_sat' :
        _result = run_guided_sat_algo(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit, solver_type)    

    elif _algo_type == 'guided_sat_enum' :
        _result = run_guided_sat_enum_algo(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit, solver_type)    

    #Decision Tree Algorithm.
    elif _algo_type == 'dt' :
        _result = run_dt_algo(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit)
        
    elif _algo_type == 'scikit_dt':
        _result = run_scikit_dt_algo(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit)        
        
    #SMT Algorithm.
    elif _algo_type == 'fin_adt' :
        def_file = os.path.abspath('resources/fin-adt.smt2')
        sygus_def_file = open(def_file, 'rt')
        _result = run_adt_fin_algo(sygus_def_file, _size, _count, trace_file, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit)

    elif _algo_type == 'adt_sygus' :
        def_file = os.path.abspath('resources/adt-sygus.sy')
        sygus_def_file = open(def_file, 'rt')
        _result = run_adt_sygus_algo(sygus_def_file, _size, _count, trace_file, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit)
        
    elif _algo_type == 'bv_sygus' :
        def_file = os.path.abspath('resources/bv-sygus.sy')
        sygus_def_file = open(def_file, 'rt')
        _result = run_bv_sygus_algo(sygus_def_file, _size, _count, trace_file, benign_traces, rejected_traces, unary_operators, binary_operators, max_trace_length, AP_Lit)

    else:
        logging.warn('Correct Synthesizing algorithm is not selected! -- Please select one')    
    
    if _result == None or len(_result) == 0:
        logging.info('Unable to Synthesize any Formula!')
    else:
        logging.info('Synthesized Signatures:')
        fml_count = 1
        for synf in _result: 
            synFml = '(%d) %s'%(fml_count, synf)
            
            result_file.write(synFml+'\n')
            logging.info(synFml)
            
            fml_count += 1
        result_file.close()

    return _result    

