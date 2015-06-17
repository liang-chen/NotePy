import glob

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []
        self.ran = (0,0)
        self.attribute = {}
    def add_child(self, child):
        self.children.append(child)
    def set_range(self,r):
        self.ran = r
    def add_attribute(self,key,attribute):
        if key not in self.attribute:
            self.attribute.update({key:[]})
        if key == 'o': #onset is used to order symbols, in integer type
            att = int(attribute)
        elif key == 'd':
            inp = attribute.strip()
            ilist = inp.split('/')
            if len(ilist) == 2:
                att = float(ilist[0])/float(ilist[1])
            elif len(ilist) == 1:
                att = float(ilist[0])
            else:
                error('Cannot handle this type of duration.')
                att = 0
        elif key == 'p': #for pitch
            pc = attribute[0].lower()
            ran = int(attribute[1])
            m = (ran+1)*12 + glob.pitch_index[pc]
            if len(attribute) == 2:
                att = (m,'none')
            elif len(attribute) >= 3:
                att = (m,attribute[2:])
            else:
                error('Error in parsing pitch '+attribute)
        else:
            att = attribute
        self.attribute[key].append(att)
    def display(self,level):
        print "\t"*level + repr(self.value)+"\n"
        for child in self.children:
            child.display(level+1)
    
class Tree:
    def __init__(self,root=None):
        if root is None:
            self.root = None
            self.num = 0
            self.nodes = []
        else:
            self.root = root
            self.num = 1
            self.nodes = [root]
    def add_node(self,node):
        self.nodes.append(node)
        if self.num == 0:
            self.root = node
        self.num = self.num + 1
    def display(self):
        self.root.display(0)

class Primitive:
    def __init__(self, name, num = 0, onset = -1):
        self.name = ''.join(name)
        self.locs = [[[-1,0],[-1,0]], [[-1,0],[-1,0]]] #in the form of [loc1: (i,ishift, j, jshift), loc2: (i, ishift, j, jshift)]
        self.num = num #num of locs
        self.onset = onset#by default, the onset is not set
        self.symbol = -1
    def set_parm(self,parm,index,ij):#input the nth loc's i/j parm, n = index, 0 for i and 1 for j, index = 0->1 left->rite or top -> bot
        self.locs[index][ij] = [parm[0], parm[1]]
    def set_num(self,num):
        self.num = num
    def set_onset(self,onset):
        self.onset = onset
    def set_sym_index(self,sym_index):
        self.symbol = sym_index
    def set_loc(self,loc_parm,index):#input the nth loc's parms
        self.locs[index][0] = [loc_parm[0][0], loc_parm[0][1]] #i
        self.locs[index][1] = [loc_parm[1][0], loc_parm[1][1]] #j
    def __lt__(self, other):
        return self.onset < other.onset

class Parm:
    def __init__(self, value, tp = 'c'):
        self.tp = tp;#unset yet, "c" for constant, "h" for horizontal, "v" for vertical, "d" for dependent
        self.value = value
        self.dependent = []
    def set_value(self,value):
        self.value = value
    def set_type(self,tp):
        self.tp = tp
    def set_dependent(self,parms,weights):
        self.dependent = zip(parms,weights)
    def update_value(self):
        self.value = sum([parm.value * weight for (parm,weight) in self.dependent])
    def update_weights(self,weights):
        parms = zip(*self.dependent)[0]
        self.dependent = zip(parms,weights)

class Edge:
    def __init__(self,prim1,prim2,l1,l2,tp,ideal):
        self.prim1 = prim1
        self.prim2 = prim2
        self.loc1 = l1
        self.loc2 = l2
        self.tp = tp #"h" for prim 1 is on the left of prim2, "v" for prim1 is on the top of prim2
        self.ideal = ideal

class Graph:
    def __init__(self):
        self.prims = []
        self.num = 0
        self.parms = []
        self.edges = []
        self.dep = []
    def add_prim(self,prim):
        self.prims.append(prim)
        self.num = self.num+1
    def add_parm(self,parm):
        self.parms.append(parm)
        return len(self.parms)-1#return the index
    def add_edge(self,prim1,prim2,loc1,loc2,tp,ideal):
        edge = Edge(prim1,prim2,loc1,loc2,tp,ideal)
        self.edges.append(edge)
    def add_dep(self,prim1,prim2,tp):#prim1 is dependent on prim2
        self.dep.append([prim1,prim2,tp])#tp = 't','b' and numbers for top, bottom and parallel
