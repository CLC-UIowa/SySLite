class PLTLFormula:
    
    def __init__(self, fml):
        self.label = fml[0]
        self.left = fml[1]
        try:
            self.right = fml[2]
        except:
            self.right = None
    
    def __hash__(self):
        return hash((self.label, self.left, self.right))

    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.label == other.label and self.left == other.left and self.right == other.right
        
    def __repr__(self):
        if self.left == None and self.right == None:
            return self.label        
        # if a node has only one child, that is the left one
        elif self.left != None and self.right == None:
            return self.label + '(' + self.left.__repr__() + ')'
        
        elif self.left != None and self.right != None:
            return   self.label + '(' + self.left.__repr__() + ',' + self.right.__repr__() + ')'  
    
    def _isLeaf(self):
        return self.right == None and self.left == None
    
    def getAllNodes(self):
        leftNodes = []
        rightNodes = []
        
        if self.left != None:
            leftNodes = self.left.getAllNodes()
        if self.right != None:
            rightNodes = self.right.getAllNodes()
        return [self] + leftNodes + rightNodes
    