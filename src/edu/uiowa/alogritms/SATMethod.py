'''
Copyright (c) 2020, Board of Trustees of the University of Iowa.
All rights reserved.

Use of this source code is governed by a BSD 3-Clause License that
can be found in the LICENSE file.
'''

from edu.uiowa.encoder.SATEncoder import SATEncoder
from edu.uiowa.encoder.GuidedSATEncoder import GuidedSATEncoder
from edu.uiowa.strategies.TopologicalGraph import topology_graph
from edu.uiowa.solver.RunSolver import SATSolver
from edu.uiowa.utils.Printer import eval_result

import timeit
import logging


def run_sat_algo(_length, _count, benign_traces, rejected_traces, unary_ops =  ['!', 'Y', 'O', 'H', 'G'], binary_ops = ['S','&', '|', '=>'], AP_Lit = None, solver_name = "z3"): 
    
    start_time = timeit.default_timer()

    sample_trace = benign_traces[0]
    
    sat_en = SATEncoder(_length, sample_trace.vars, unary_ops, binary_ops, AP_Lit)
    
    #Encoding shape of the Formula
    logging.info('Encoding Shape Constraints...')    
    shape_fml = sat_en.encode_shape()

    sat_solver = SATSolver(solver_name)
    
    sat_solver.assert_cls(shape_fml)
        

    logging.info('Encoding Benign Traces Constraints...')
    for trace in benign_traces:
        _enc_fml = sat_en.encode_trace(trace, True)
        sat_solver.assert_cls(_enc_fml)
    
    logging.info('Encoding Rejected Traces Constraints...')    
    for trace in rejected_traces:
        _enc_fml = sat_en.encode_trace(trace, False)
        sat_solver.assert_cls(_enc_fml)
    
    logging.debug('Constraint solver is running...')
    
    model = sat_solver.get_model()
    
    _result = []
    while model is not None:
        
        pLTL_fml = sat_en.m2f(_length - 1, model)
        
        if not pLTL_fml in _result:
            _result.append(pLTL_fml)

        pmodel = sat_en.dag_shape(model)
        model = sat_solver.enum_model(pmodel)    
        
        logging.info('Extracted formula %s'%(pLTL_fml))
        
        stop = timeit.default_timer()
        elasped_time = ('%.2f')%(stop - start_time)
    
        logging.info('Time: %s seconds'%(elasped_time))

        if _count <= len(_result):
            break
        
    
    logging.debug('Checking Synthesize pLTL Formulae...')
    
    eval_result(_result, benign_traces, rejected_traces, _count)
    logging.info('Synthesized Signatures: %s'%(_result))
    
    sat_solver.clear_solver()
    
    return _result


def run_enum_sat_algo(_length, _count, benign_traces, rejected_traces, unary_ops =  ['!', 'Y', 'O', 'H'], binary_ops = ['S','&', '|', '=>'], AP_Lit = None, solver_type = 'z3'): 

    start_time = timeit.default_timer()
    
    _results = []
    size_counter = 1
    p_count = _count

    while len(_results) <= p_count:
        
        fixed_length_result = run_sat_algo(size_counter, _count, benign_traces, rejected_traces, unary_ops, binary_ops, AP_Lit, solver_type)
        fm_counter = len(fixed_length_result) - 1
        
        while fm_counter >= 0: 
            
            fml = fixed_length_result[fm_counter]
            
            if not fml in _results:  
                _results.append(fml)

            fm_counter -= 1

            if(len(_results) >= p_count):
                break            
            

        if(len(fixed_length_result) >= _count):
            break            

        size_counter += 1

        _count -=   len(fixed_length_result) 


    stop = timeit.default_timer()
    elasped_time = ('%.2f')%(stop - start_time)
    
    logging.info('Total Running Time: %s seconds'%(elasped_time))

    logging.debug('Checking Synthesize pLTL Formulae...')

    eval_result(_results, benign_traces, rejected_traces, _count)
            
    return _results    


def run_sat_algo_bound(_length, _count, benign_traces, rejected_traces, unary_ops =  ['!', 'Y', 'O', 'H'], binary_ops = ['S','&', '|', '=>'], AP_Lit = None, solver_type = 'z3'): 

    start_time = timeit.default_timer()
    
    _results = []

    c = len(rejected_traces)
    while c >= 1:
        
        tmp_results = run_enum_sat_algo(_length, _count, benign_traces, rejected_traces, unary_ops, binary_ops, AP_Lit, solver_type)
        fml = tmp_results[0]
        logging.info('Formula: %s'%(fml))
        logging.info('Rejected Traces count: %d'%(c))
        output = (fml,c)
        _results.append(output)
         
        rejected_traces.pop()   
        c = len(rejected_traces)



#    stop = timeit.default_timer()
#    elasped_time = ('%.2f')%(stop - start_time)
    
#    logging.info('Total Running Time: %s seconds'%(elasped_time))

            
    return _results    

def run_guided_sat_enum_algo(_length, _count, benign_traces, rejected_traces, unary_ops =  ['!', 'Y', 'O', 'H'], binary_ops = ['S','&', '|', '=>'], AP_Lit = None, solver_type = 'z3'): 
    
    start_time = timeit.default_timer()
    
    _results = []
    
    sample_trace = benign_traces[0]
    size_counter = sample_trace.vars
    p_count = _count
    
    while len(_results) <= p_count:
        fixed_length_result = run_guided_sat_algo(size_counter, _count, benign_traces, rejected_traces, unary_ops, binary_ops, AP_Lit, solver_type)
        
        fm_counter = len(fixed_length_result) - 1
        
        while fm_counter >= 0: 
            fml = fixed_length_result[fm_counter]
            
            if not fml in _results:  
                _results.append(fml)
                
            fm_counter -= 1

            if(len(_results) >= p_count):
                break            

        if(len(fixed_length_result) >= _count):
            break            

        size_counter += 1
        _count -=   len(fixed_length_result) 

    stop = timeit.default_timer()
    elasped_time = ('%.2f')%(stop - start_time)
    logging.info('Total Running Time: %s seconds'%(elasped_time))

    logging.debug('Checking Synthesize pLTL Formulae...')

    eval_result(_results, benign_traces, rejected_traces, _count)
            
    return _results   

def run_guided_sat_algo(_length, _count, benign_traces, rejected_traces, unary_ops =  ['!', 'Y', 'O', 'H'], binary_ops = ['S','&', '|', '=>'], AP_Lit = None, solver_name = "z3"): 
    
    start_time = timeit.default_timer()

    sample_trace = benign_traces[0]
    
    if _length < sample_trace.vars:
        logging.warn('In correct size, please correct the size > |AP|')
        exit()
        
    sat_en = GuidedSATEncoder(_length, sample_trace.vars, unary_ops, binary_ops, AP_Lit)
    
    root = _length 

    logging.info('Generate Graph Topology...')
    partial_DAGs = topology_graph(root, sample_trace.vars+1) 

    logging.info('Encoding Shape Constraints...')    
    
    shape_fml = sat_en.encode_shape()
    
    sat_solver = SATSolver(solver_name)
    
    sat_solver.assert_cls(shape_fml)
        
    logging.info('Encoding Benign Traces Constraints...')
    for trace in benign_traces:
        _enc_fml = sat_en.encode_trace(trace, True)
        sat_solver.assert_cls(_enc_fml)
    
    logging.info('Encoding Rejected Traces Constraints...')    
    for trace in rejected_traces:
        _enc_fml = sat_en.encode_trace(trace, False)
        sat_solver.assert_cls(_enc_fml)

    
    
    ap_cls = sat_en.get_AP_cls()
        
    sat_solver.assert_cls(ap_cls)
    
    _result = []
    
    for p_dag  in partial_DAGs:
        
        d = sat_en.get_partial_dag_cls(p_dag)
        
        _resultf = assert_pdg(sat_solver, d, sat_en, _length)

        
        if len(_resultf) > 0:
            _result.extend(_resultf)

            stop = timeit.default_timer()
            elasped_time = ('%.2f')%(stop - start_time)
    
            logging.info('Time: %s seconds'%(elasped_time))
            logging.debug('Checking Synthesize pLTL Formulae...')
            
            eval_result(_result, benign_traces, rejected_traces, _count)
    
#            logging.info('Synthesized Signatures: %s'%(_result))
            
    
    for p_dag  in partial_DAGs:
        
        d = sat_en.get_partial_dag_cls_reverse(p_dag)
        
        _resultf = assert_pdg(sat_solver, d, sat_en, _length)

        if len(_resultf) > 0:
            _result.extend(_resultf)

            stop = timeit.default_timer()
            elasped_time = ('%.2f')%(stop - start_time)
    
            logging.info('Time: %s seconds'%(elasped_time))
            logging.debug('Checking Synthesize pLTL Formulae...')
        
            eval_result(_result, benign_traces, rejected_traces, _count)
        
#            logging.info('Synthesized Signatures: %s'%(_result))
    
    return _result


def assert_pdg(sat_solver, d, sat_en, _length):
    
    sat_solver.add_cls(d, 1)
    logging.debug('Constraint solver is running...')
    model = sat_solver.get_model()
        
    _result = []
        
    if model is not None:
        
        pLTL_fml = sat_en.m2f(_length, model)
    
        if not pLTL_fml in _result:
            _result.append(pLTL_fml)

        logging.info('Extracted formula %s'%(pLTL_fml))
 
            
    sat_solver.remove_cls(1)
    
    return _result

def assert_pdg_reverse(sat_solver, d, sat_en, _length):
    
    sat_solver.add_cls(d, 1)
    logging.debug('Constraint solver is running...')
    model = sat_solver.get_model()
        
    _result = []
        
    if model is not None:
        pLTL_fml = sat_en.m2f(_length, model)
    
        if not pLTL_fml in _result:
            _result.append(pLTL_fml)

        logging.info('Extracted formula %s'%(pLTL_fml))
 
    sat_solver.remove_cls(1)
    
    return _result
    
    