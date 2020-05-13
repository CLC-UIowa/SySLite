'''
Created on Nov 26, 2019

@author: marif
'''
from edu.uiowa.parser.Formula import PLTLFormula

def unique_vals(rows, col):
#    """Find the unique values for a column in a dataset."""
    return set([row[col] for row in rows])

def class_counts(rows):
    """Counts the number of each type of example in a dataset."""
    counts = {}  # a dictionary of label -> count.
    for row in rows:
        # in our dataset format, the label is always the last column
        label = row[-2]
        if label not in counts:
            counts[label] = 0
        counts[label] += 1
    return counts

def info_gain(left, right, current_uncertainty):
    """Information Gain.

    The uncertainty of the starting node, minus the weighted impurity of
    two child nodes.
    """
    p = float(len(left)) / (len(left) + len(right))
    return current_uncertainty - p * gini(left) - (1 - p) * gini(right)

def partition(rows, question):
    """Partitions a dataset.

    For each row in the dataset, check if it matches the question. If
    so, add it to 'true rows', otherwise, add it to 'false rows'.
    """
#    print(rows, question)
    true_rows, false_rows = [], []
    for row in rows:
        if question.match(row):
            true_rows.append(row)
        else:
            false_rows.append(row)
    return true_rows, false_rows


def gini(rows):
    """Calculate the Gini Impurity for a list of rows.

    There are a few different ways to do this, I thought this one was
    the most concise. See:
    https://en.wikipedia.org/wiki/Decision_tree_learning#Gini_impurity
    """
    counts = class_counts(rows)
    impurity = 1
    for lbl in counts:
        prob_of_lbl = counts[lbl] / float(len(rows))
        impurity -= prob_of_lbl**2
    return impurity



def find_best_split(rows):
    """Find the best question to ask by iterating over every feature / value
    and calculating the information gain."""
    best_gain = 0  # keep track of the best information gain
    best_question = None  # keep train of the feature / value that produced it
    current_uncertainty = gini(rows)
    n_features = len(rows[0]) - 2  # number of columns

    for col in range(n_features):  # for each feature
        
        values = unique_vals(rows, col) # unique values in the column

        for val in values:  # for each value

            question = Question(col, val)
#            
            # try splitting the dataset
            true_rows, false_rows = partition(rows, question)
            #print('Questions:',question, best_gain)
            # Skip this split if it doesn't divide the
            # dataset.

            if len(true_rows) == 0 or len(false_rows) == 0:
                continue

            # Calculate the information gain from this split
            gain = info_gain(true_rows, false_rows, current_uncertainty)
            # You actually can use '>' instead of '>=' here
            # but I wanted the tree to look a certain way for our
            # toy dataset.
            if gain >= best_gain:
                best_gain, best_question = gain, question
                
            
                

    return best_gain, best_question

def build_tree(rows):

# Try partitioing the dataset on each of the unique attribute,
# calculate the information gain,
# and return the question that produces the highest gain.
    gain, question = find_best_split(rows)

# Base case: no further info gain
# Since we can ask no further questions,
# we'll return a leaf.
    if gain == 0:
        return Leaf(rows)

# If we reach here, we have found a useful feature / value
# to partition on.
    true_rows, false_rows = partition(rows, question)

# Recursively build the true branch.
    true_branch = build_tree(true_rows)

# Recursively build the false branch.
    false_branch = build_tree(false_rows)

# Return a Question node.
# This records the best feature / value to ask at this point,
# as well as the branches to follow
# dependingo on the answer.
    return Decision_Node(question, true_branch, false_branch)


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
    

def classify(row, node):
    """See the 'rules of recursion' above."""

    # Base case: we've reached a leaf
    if isinstance(node, Leaf):
        return node.predictions

    # Decide whether to follow the true-branch or the false-branch.
    # Compare the feature / value stored in the node,
    # to the example we're considering.
    if node.question.match(row):
        return classify(row, node.true_branch)
    else:
        return classify(row, node.false_branch)


class Question:
    """A Question is used to partition a dataset.

    This class just records a 'column number' (e.g., 0 for Color) and a
    'column value' (e.g., Green). The 'match' method is used to compare
    the feature value in an example to the feature value stored in the
    question. See the demo below.
    """

    def __init__(self, column, value):
        self.column = column
        self.value = value

    def match(self, example):
        # Compare the feature value in an example to the
        # feature value in this question.
        val = example[self.column]

        if val > 0:
            return True
        else:
            return False

    def qid(self):
        return self.column

#    def __repr__(self):

#        return "Is %s" % (self.column)
        

class Decision_Node:
    """A Decision Node asks a question.

    This holds a reference to the question, and to the two child nodes.
    """

    def __init__(self,
                 question,
                 true_branch,
                 false_branch):
        self.question = question
        self.true_branch = true_branch
        self.false_branch = false_branch
        
class Leaf:
    """A Leaf node classifies data.

    This holds a dictionary of class (e.g., "Apple") -> number of times
    it appears in the rows from the training data that reach this leaf.
    """

    def __init__(self, rows):
        self.predictions = class_counts(rows)
        self.rows = rows

    def __repr__(self):
        row_ids = []
        for r in self.rows:
            row_ids.append(str(r[-1]))
        return ''.join(row_ids)        
        



class DecisionTree:

    def __init__(self, t_data, f_features):
        self.training_data = t_data
        self.features = f_features
        self.d_tree = None
#        self.paths = []
    def build_dt(self):
        self.d_tree = build_tree(self.training_data)
        return self.d_tree


    def dt_classify(self, row):
        return classify(row, self.d_tree)
        

    def print_tree(self, node, spacing=""):
        """World's most elegant tree printing function."""
    
        # Base case: we've reached a leaf
        if isinstance(node, Leaf):
            print (spacing + "Leaf:", node.predictions)
            for row_id in node.rows:
                print(spacing + 'Trace(%s)'%(row_id[-1]))
            return
        
        # Print the question at this node
        q = node.question
        print(spacing + str(self.features[q.qid()]))
        
        # Call this function recursively on the true branch
        print (spacing + '--> T')
        self.print_tree(node.true_branch, spacing + "  ")
        
        # Call this function recursively on the false branch
        print (spacing + '--> F')
        self. print_tree(node.false_branch, spacing + "  ")
        

    def compute_paths(self, node, stack, paths):
        

        if isinstance(node, Leaf):
            #Proposition.
            p  = stack[:]
            p.append(node.predictions) 
            paths.append(p)
#            print()
#            paths.append()
            if len(stack) != 0:
                stack.pop()            
#            print(paths)             
            return

        q = node.question
        v = (self.features[q.qid()], True)
        stack.append(v)


        self.compute_paths(node.true_branch, stack, paths)
                            
        q = node.question
        v = (self.features[q.qid()], False)
        stack.append(v)
        
        self.compute_paths(node.false_branch, stack, paths)
        
        if len(stack) != 0:
            stack.pop()
        else:
            return paths    
        
        
    def print_leaf(self, counts):
        """A nicer way to print the predictions at a leaf."""
        total = sum(counts.values()) * 1.0
        probs = {}
        for lbl in counts.keys():
            probs[lbl] = str(int(counts[lbl] / total * 100)) + "%"
        return probs

    def path2fml(self, path, idx=0):
        
        p = path[idx]
        
        if idx == len(path) - 1:
            return p
        
        if p[1]:
            path[idx] = p[0]
    
        else:
            path[idx] = '!' + p[0]
            
        self.path2fml(path, idx + 1)
        
        return path    

    def isLeaf(self, node):
        
        if isinstance(node, Leaf):
            return True
        
        return False

