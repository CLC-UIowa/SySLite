from sklearn.metrics import accuracy_score 
from sklearn import tree

from sklearn.tree import DecisionTreeClassifier
import numpy as np

from graphviz import Source

#from scikit.tree import export_text
from sklearn.tree.export import export_text

from edu.uiowa.parser.Formula import PLTLFormula

import logging

def path2fml(path, idx=0):
    
    p = path[idx]
    
    if idx == len(path) - 1:
        return p
    
    if p[1]:
        path[idx] = p[0]

    else:
        path[idx] = '!(' + p[0] + ')'
        
    path2fml(path, idx + 1)
    
    return path    


def or_fml(path):
    
#    print('PATH:', path)
    
    if len(path) == 1:
        return and_fml(path[0])
   
    left = and_fml(path[0])
    right  = or_fml(path[1:])
    
    
    return PLTLFormula(['|', left, right])

def and_fml(path):

    if len(path) == 1:        
        return PLTLFormula([path[0], None , None])
   
    left = PLTLFormula([path[0], None , None])

    return PLTLFormula(['&', left, and_fml(path[1:])])


def tree_to_phi(tree, feature_names):
    tree_ = tree.tree_
    classes = tree.classes_
    
    feature_name = [
        feature_names[i] if i != -2 else "undefined!"
        for i in tree_.feature
    ]
    

    def eval_paths(node, stack, paths):
        
    
        if tree_.feature[node] == -2:
            #Proposition.
            p  = stack[:]
            cls_index = np.argmax(tree_.value[node][0])
            p.append(classes[cls_index]) 
            paths.append(p)

            if len(stack) != 0:
                stack.pop()            
    #            print(paths)             
            return
        
        v = (feature_name[node], False)
        stack.append(v)
    

        eval_paths(tree_.children_right[node], stack, paths)
                            
        v = (feature_name[node], True)
        stack.append(v)
        
        eval_paths(tree_.children_left[node], stack, paths)
        
        if len(stack) != 0:
            stack.pop()
        else:
            return paths    

    all_paths = eval_paths(0,[],[])
    
#    print('ALL PATHS',all_paths)
    true_paths = []
    

    if all_paths: 
        for p in all_paths:
                                 
            phi = path2fml(p)
#            print('PHI**', phi)
            
            value = phi.pop()
            
#            print('Value:',value)
            if value == 'True':
                #phi.push(value)
                true_paths.append(phi)
#                break;
#        print('++++++++True Paths:', true_paths)   
        
        _fml = or_fml(true_paths)
        
#        print('++++++++Formula:', _fml)
        
        return _fml    

def scikit_cart(features, X_data, Y_data):

    #criterion='gini'
    
    tree.DecisionTreeClassifier().fit(X_data, Y_data)
    clf = tree.DecisionTreeClassifier().fit(X_data, Y_data)
#    tree = clf

    Y_pred = clf.predict(X_data)

    if len(features) != 1:
        dt_tree = export_text(clf, feature_names=features)
        print('Decision Tree:')
        print(dt_tree)


#     outputFile = open('graph.pdf', 'w')
#     treeDotFormat = tree.export_graphviz(clf, out_file=outputFile, feature_names = features, filled=True)
#     print('Tree DOT Format:', treeDotFormat)
#     outputFile.close()
#     s = Source.from_file('graph.pdf')
#     s.view()

    synz_fml = tree_to_phi(clf, features)
    
#     print('***Synthesize Formula:',synz_fml)
#     print('***Feature List:', features)
#     print('***Feature List Size', len(features))
    
    logging.info('Synthesized formula: %s'%(synz_fml))
    logging.info("Accuracy:%f"%(accuracy_score(Y_data, Y_pred)))

    return synz_fml


if __name__ == '__main__':

    features = ['O(p2)', 'O(S(p2,p2))', 'O(H(p2))', 'O(|(p2,p2))', 'O(&(p2,p2))']

    features = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']
    
    Y_data = ['True', 
              'True', 
              'True', 
              'False', 
              'False', 
              'False'
             ]

    X_data = [[1, 1, 1, 1, 1,0], 
              [0, 0, 1, 1, 0,0], 
              [0, 1, 0, 1, 1,0], 
              [0, 0, 0, 0, 0,1], 
              [1, 0, 1, 1, 0,0], 
              [1, 1, 1, 1, 0,0]
              ]
    
    scikit_cart(features, X_data, Y_data)

