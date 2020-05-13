from edu.uiowa.strategies.DTClassifer import stratgey_beta, stratgey_gamma, training_dataset, prepare_dataset
from edu.uiowa.encoder.CART import DecisionTree, or_fml, path2fml
from edu.uiowa.encoder.ScikitCART import scikit_cart
from edu.uiowa.parser.LarkParser import pLTLParser
from edu.uiowa.utils.Printer import eval_result

import timeit
import logging

def run_scikit_dt_algo(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit):
    
    start_time = timeit.default_timer()
    _result = []    
    result_flag = False

    _features = stratgey_gamma(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit)

    x_dataset, y_dataset = prepare_dataset(_features, benign_traces, rejected_traces)
    
    logging.debug('Training Data set:%s'%(x_dataset))    
    logging.debug('Size of Training Data set%s'%(len(x_dataset)))


    _features = list(map(str, _features))
    
    parser = pLTLParser()

    if len(_features) != 0:
        
        synz_fml = scikit_cart(_features,x_dataset, y_dataset)
        f = parser.parse(str(synz_fml))

        _result.append(f)
        
        result_flag = eval_result(_result, benign_traces, rejected_traces, _count)
        

    stop = timeit.default_timer()
    elasped_time = ('%.2f')%(stop - start_time)
    
    logging.info('Total Running Time Time: %s seconds'%(elasped_time))
    logging.debug('Checking Synthesize pLTL Formulae...')
    
    return _result    
            
            
def run_dt_algo(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit):

    start_time = timeit.default_timer()

    _result = []
          
    _features = stratgey_beta(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit)
    
    _dataset = training_dataset(_features, benign_traces, rejected_traces)
    
    logging.debug('Training Data set%s'%(_dataset))    
    logging.debug('Size of Training Data set%s'%(len(_dataset)))


    _features = list(map(str, _features))
    logging.info(_features)
       
    my_dt = DecisionTree(_dataset, _features)
    
    my_tree = my_dt.build_dt()

    for row in _dataset:        
        leaf = my_dt.dt_classify(row)
        
        logging.debug("Actual: Trace(%d) Predicted: %s" %(row[-1], leaf))

    if my_dt.isLeaf(my_tree):
        logging.debug('Only Single Leaf Node, ... any feature can be used...')
    
        
    else:
        paths = my_dt.compute_paths(my_tree, [], [])
                
        true_paths = []
        parser = pLTLParser()
        
        #Formulate paths.
        for p in paths:
                             
            phi = path2fml(p)
            
            values = phi.pop()
            max_value = max(values, key=values.get)
            #Prune Path with True in Leaf.
            if max_value == 'True':    
                true_paths.append(phi)
                
        synz_fml = or_fml(true_paths)
        
        f = parser.parse(str(synz_fml))
        
        _result.append(f)
    
        stop = timeit.default_timer()
        elasped_time = ('%.2f')%(stop - start_time)
        
        logging.info('Total Running Time Time: %s seconds'%(elasped_time))
        logging.debug('Checking Synthesize pLTL Formulae...')
    
        eval_result(_result, benign_traces, rejected_traces, _count)
        
    return _result       