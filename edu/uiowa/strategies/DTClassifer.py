from edu.uiowa.alogritms.SATMethod import run_sat_algo, run_enum_sat_algo

import itertools
import timeit
import random
import logging

def training_dataset(features, beningn_traces, rejected_traces):
    
    training_data = []
    
    for trace in beningn_traces:        
        pos_data = []
        
        for phi in features:
            
            sat = trace.check_truth(phi)
            logging.debug('Trace(%s) - pLTL(%s) - %s'%(trace.Id, phi, sat))
            
            if sat:
                pos_data.append(1)
            else:
                pos_data.append(-1)
                logging.debug('Check for possible Error in Generating DataSet - (Positive Examples)')
        #Label       
        pos_data.append('True')
        #Trace ID
        pos_data.append(int(trace.Id))
                
        training_data.append(pos_data)

    for trace in rejected_traces:        
        neg_data = []
        
        for phi in features:
            
            sat = trace.check_truth(phi)
            logging.debug('Trace(%s) - pLTL(%s) - %s'%(trace.Id, phi, sat))
            
            if not sat:
                neg_data.append(-1)
            else:
                neg_data.append(1)
                logging.debug('Check for possible Error in Generating DataSet - (Negative Examples)')
                
        neg_data.append('False')
        neg_data.append(int(trace.Id))
        training_data.append(neg_data)

            
    return training_data

def prepare_dataset(features, beningn_traces, rejected_traces):
    
    x_data = []
    y_data = []
    
    for trace in beningn_traces:        
        pos_data = []
        
        for phi in features:
            
            sat = trace.check_truth(phi)
            logging.debug('Trace(%s) - pLTL(%s) - %s'%(trace.Id, phi, sat))
            
            if sat:
                pos_data.append(0)
            else:
                pos_data.append(1)
                
        x_data.append(pos_data)
        y_data.append('True')
        
    for trace in rejected_traces:    
            
        neg_data = []
        
        for phi in features:
            
            sat = trace.check_truth(phi)
            logging.debug('Trace(%s) - pLTL(%s) - %s'%(trace.Id, phi, sat))
            
            if sat:
                neg_data.append(0)
            else:
                neg_data.append(1)
    
        x_data.append(neg_data)
        y_data.append('False')
        
    logging.debug('Training Data set%s'%(x_data))    
            
    return x_data, y_data
    
def stratgey_alpha(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit):    
    #Product Traces
    pair_traces = list(itertools.product(benign_traces, rejected_traces))
    
    logging.debug('Number of Pairs:%d'%(len(pair_traces)))
    
    population_size = len(pair_traces)
    
    #Failed Feature Computation Threshold
    f_threshold = -1
    #select k pairs.    
    k = 3
    
    features = set()
    
    while (population_size != 0 and f_threshold < 10):
        
        if population_size < k:
            k = population_size 
        
        k_sample = random.sample(pair_traces, k)

        pos_traces = []
        neg_traces = []
        
        for tr in k_sample:
            
            #Strategy 1
            #Combine unique pair of positive & negative traces            
            if tr[0] not in pos_traces: 
                pos_traces.append(tr[0])
            if tr[1] not in neg_traces:
                neg_traces.append(tr[1])
                            
            
        logging.debug("+ve Trace%s"%(pos_traces))
        logging.debug("-ve Trace%s"%(neg_traces))

        #Compute SAT Formula (Features
        f_phis = run_sat_algo(_size, _count, pos_traces, neg_traces, unary_operators, binary_operators, AP_Lit)

        if len(f_phis) > 0:
             
            for tr in k_sample:
                pair_traces.remove(tr)

            for phi in f_phis:    
                print('Formula: ', phi)
            # Collecting features List
                features.add(phi)
                
        population_size = len(pair_traces)
        
        logging.debug('Number of Pairs:%d'%(population_size))
        
        f_threshold += 1
        
    return features
    

def stratgey_beta(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit):    
    #Product Traces
    pair_traces = list(itertools.product(benign_traces, rejected_traces))
    
    logging.debug('Number of Pairs:%d'%(len(pair_traces)))
    
    population_size = len(pair_traces)
    
    #Failed Feature Computation Threshold
    f_threshold = -1
    #select k pairs.    
    k = 3
    
    f_size = 1
    
    features = set()
    
    while (population_size != 0 and f_threshold < 10):
        
        if population_size < k:
            k = population_size 
        
        k_sample = random.sample(pair_traces, k)
        
        for tr in k_sample:
            pos_trace = []
            neg_trace = []
            #Strategy 2
            #Generate Feature for each pair and discard successful pairs.
            pos_trace.append(tr[0])
            neg_trace.append(tr[1])
            
            logging.debug("+ve Trace%s"%(pos_trace))
            logging.debug("-ve Trace%s"%(neg_trace))

            while True:
                f_phis = run_sat_algo(f_size, 1, pos_trace, neg_trace, unary_operators, binary_operators, AP_Lit)                    
 
                if len(f_phis) == 0:
                    f_size += 1
                else: 
                    break
            
            #Success ... add to feature list.
            if len(f_phis) > 0:
                 
                pair_traces.remove(tr)
    
                for phi in f_phis:    
                    logging.debug('Formula: %s'%(phi))
                # Collecting features List
                    features.add(phi)
                
        population_size = len(pair_traces)
        
        logging.debug('Number of Pairs:%d'%(population_size))
        
        f_threshold += 1
        
    logging.debug('Features:%s'%(features))
    logging.debug('Features Size:%d'%(len(features)))
         
    return features       

def weighted_choice(weighted_dict, items):
    w_choice = random.choices(list(weighted_dict.keys()),list(weighted_dict.values()), k = items)
    return list(set(w_choice))


def adjust_weights(weighted_dict, trace, trace_count):

    weighted_dict[trace] = trace_count

def update_split_dictionary(phi, splitDict, pos_prob_dict, neg_prob_dict):

    logging.debug('Updating Dictionary*********')
    pos_dict_size = len(pos_prob_dict.keys())
    neg_dict_size = len(neg_prob_dict.keys())
    
    pos_traces = []
    neg_traces = []

    logging.debug('Before split Dictionary%s'%(splitDict))
    for trace_pair in splitDict:
    
        pos_sat = trace_pair[0].check_truth(phi)         
        neg_sat = trace_pair[1].check_truth(phi)
       
        if pos_sat and not neg_sat:
            splitDict[trace_pair] = True
        
        #Incorrect +ve classification
        if not pos_sat:
            pos_traces.append(trace_pair[0])  
            adjust_weights(pos_prob_dict, trace_pair[0], pos_dict_size)          
        #Incorrect -ve classification    
        if neg_sat:
            neg_traces.append(trace_pair[1])
            adjust_weights(neg_prob_dict, trace_pair[1], neg_dict_size)
    
    logging.debug('After split Dictionary%s'%(splitDict))       


def reset_weights(list_length):
    w_list = []
    for w in range(1, list_length + 1):
        w_list.append(w)
    return  w_list    


def stratgey_gamma(_size, _count, benign_traces, rejected_traces, unary_operators, binary_operators, AP_Lit):

    #Create Separation Dictionary.
    splitDict = {sp: False for sp in itertools.product(benign_traces, rejected_traces)} 
    
    features = set()
                
    logging.debug('Split Dictionary:%s'%(splitDict))
        
    prob_weight = reset_weights(len(benign_traces))
    
    logging.debug('weights%s'%(prob_weight))

    k_traces = 1
        
    pos_prob_dict = dict(zip(benign_traces, prob_weight))
    neg_prob_dict = dict(zip(rejected_traces, prob_weight))
    
    
    #Failed Feature Computation Threshold
    f_threshold = -1    
    
    logging.debug('Termination condition : %s'%(min(splitDict.values())))
    
    f_size = 1 
    #Termination Criteria.
    while not min(splitDict.values()):
            
        k_pos_samples = weighted_choice(pos_prob_dict, k_traces)
        logging.debug('K Positive Samples%s'%(k_pos_samples))
        k_neg_samples = weighted_choice(neg_prob_dict, k_traces)
        logging.debug('K Negative Samples%s'%(k_neg_samples))

        #Compute SAT Formula (Features
        #Store Last stored formula length.        
        while True:
            
            f_phis = run_sat_algo(f_size, 1, k_pos_samples, k_neg_samples, unary_operators, binary_operators, AP_Lit)
            
            if len(f_phis) == 0 and f_size <= _size:
                f_size += 1
            else: 
                break
            
        
        if len(f_phis) > 0:
        #Success ... add to feature list.
            phi = f_phis[0]
            features.add(phi)


            update_split_dictionary(phi, splitDict, pos_prob_dict, neg_prob_dict)
        
        else:
            if(f_threshold > 1000):
                logging.warn('No perfect splitting features found!!!')
                break
        
        f_threshold += 1
    
    if min(splitDict.values()):
        logging.info('Splitting feature Found!')
        
    return features


           
            