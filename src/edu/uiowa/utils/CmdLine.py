'''
Copyright (c) 2020, Board of Trustees of the University of Iowa.
All rights reserved.

Use of this source code is governed by a BSD 3-Clause License that
can be found in the LICENSE file.
'''
import os
import argparse

#parsing command arguments
def cmd_parser():
    
    parser = argparse.ArgumentParser()
    supported_arguments(parser)
    args = parser.parse_args()

    return args

#auxiliary function describing the program arguments
def supported_arguments(parser):

    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional arguments')
    
    required.add_argument('-s', '--size', type=int, default=3)
    required.add_argument('-n', '--number', type=int, default=1)
    required.add_argument('-a', '--algo_type', default='sat', nargs='?', choices=['sat', 'sat_enum', 'sat_bound', 'dt', 'scikit_dt', 'guided_sat','guided_sat_enum', 'fin_adt', 'adt_sygus', 'bv_sygus'])
    required.add_argument('-solver', '--solver_type', default='z3', nargs='?', choices=['z3', 'msat', 'cvc4', 'yices', 'boolector'])
    required.add_argument('-t', '--tracesFile', metavar='in-file', type=argparse.FileType('rt'), required=False)


    optional.add_argument('-r', '--result_file',  metavar='result-file', type=argparse.FileType('wt'), default='_result', required=False)    
    optional.add_argument('-dict', '--support_dict', default = False, action='store_true')
    optional.add_argument('-tg', '--random_traces', default = False, action='store_true')        
    optional.add_argument('-l', '--max_trace_length', type=int, default=3)
    optional.add_argument('-f', '--seedFile', metavar='in-file', type=argparse.FileType('rt'), required=False)


#auxiliary to obtain the input arguments
def parse_sig_options(args):    
    

    return (args.size, args.number, args.tracesFile, args.algo_type, args.support_dict, args.result_file, args.solver_type)
