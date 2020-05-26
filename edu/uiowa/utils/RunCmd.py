'''
Copyright (c) 2020, Board of Trustees of the University of Iowa.
All rights reserved.

Use of this source code is governed by a BSD 3-Clause License that
can be found in the LICENSE file.
'''

from edu.uiowa.parser.LarkParser import pLTLParser

import subprocess
from threading import Timer

import os
import logging
import timeit
import datetime

#run SyGuS-CVC4 on SyGuS specifications
def run_sygus(_adt_def, start_time, trace_file,  max_loop = 2, bv_encoding = True):
    
    #Running SyGus Command...
    currentDT = datetime.datetime.now()

    trace_file = os.path.basename(trace_file.name)
    trace_file_name, trace_ext = os.path.splitext(trace_file)
    #store unrolled specification file
    defFileName = currentDT.strftime("%Y-%m-%d_%H%M%S") + "_" + trace_file_name  +'_sygus_unrolled_encoding.sy'
    output_file = os.path.abspath(defFileName)
    
    smt2_file=open(output_file, 'w')
    smt2_file.writelines(_adt_def)
    smt2_file.close()

    smt2_file_path = os.path.basename(smt2_file.name)

    solver_path = os.path.abspath('resources/cvc4')
      
    cmd = solver_path + ' --lang=sygus2 --sygus-stream --sygus-sym-break-pbe ' + smt2_file_path
    
    cmd = list(cmd.split(' '))

    logging.info('Running SyGuS(CVC4)...')
            
    return run_cmd(cmd, max_loop, start_time, bv_encoding)
    
#run CVC4 on SMT-Lib2 specifications 
def run_smt2(_adt_def, start_time, trace_file, max_loop = 2):

    currentDT = datetime.datetime.now()
    
    trace_file = os.path.basename(trace_file.name)
    trace_file_name, trace_ext = os.path.splitext(trace_file)
    
    #store unrolled specification file   
    defFileName = currentDT.strftime("%Y-%m-%d_%H%M%S") + "_" + trace_file_name + '_fin_unrolled_encoding.smt2'
    
    #Running SMT2 Command...
    smt2_file=open(defFileName, 'w')
    smt2_file.writelines(_adt_def)
    smt2_file.close()

    smt2_file_path = os.path.basename(smt2_file.name)

    
    cmd = 'resources/cvc4 ' + smt2_file_path
    
    cmd = list(cmd.split(' '))
    logging.info('Running CVC4...')
       
    return run_cmd(cmd, max_loop, start_time, False)

#calling an external process
#def exec_cmd(cmd, time):
#    kill = lambda process: process.kill()   
#    run_cvc4 = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr=subprocess.PIPE)   
#    cvc4_timer = Timer(time, kill, run_cvc4)
#    
#    try:
#        cvc4_timer.start()
#    finally:
#        cvc4_timer.cancel()
        
#run external command          
def run_cmd(cmd, max_loop, start_time, bv_type):
    
    result = []
    parser = pLTLParser()
    
    count = 1;
    
    logging.info('Command: %s'%(cmd))
    EOF = '(error "Maximum term size (10) for enumerative SyGuS exceeded.")'
    
    #Timeout
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        for line in process.stdout:
            logging.info('Synthesized Formula Definition %s'%(line))
            
            read_data = line.decode()

            if EOF in read_data:
                continue
            elif bv_type:
                f = parser.parse_bv(read_data)
                result.append(f)
            else:#adt_type
                f = parser.parse_adt(read_data)    
                result.append(f)
                
            logging.info('Synthesized Formula %s'%(f))
            
            stop = timeit.default_timer()
            elasped_time = ('%.2f')%(stop - start_time)
            
            logging.info('Time: %s seconds'%(elasped_time))

            
            if count >= max_loop:
                process.kill()
                break;
            else:
                count += 1
                
    except Exception as e:
        logging.warn('Unable to Run CVC4...')
        logging.warn(str(e))

    return result    
