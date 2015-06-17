
from mystruct import *
import glob
#import re

def read_file(filename):
    try:
        fp = open(filename)
        txt = fp.read()
        fp.close()
    except:
        print "Error opening:", filename

    return txt

#parse content into tree
def parse_content(txt):
    _flags = glob._flags
#    print _flags
    stack = []
    tree = Tree()
    for i in range(len(txt)):
        ch = txt[i]
        if ch == '{':
            rtxt = txt[i+1:-1]
            rsplit = rtxt.replace('{',' ').replace('}', ' ').replace('\n', ' ').split()
#            print rsplit
            if len(rsplit):
                flag = rsplit[0].strip()
            else:
                flag = ""
                
            if flag in _flags:
                node = Node(flag)
                tree.add_node(node)
                stack.append((node,i))
            else:
                print "Error in parsing flag", flag
                print flag
                return None
        elif ch == '}':
            try:
                (node, left) = stack.pop()
#                print stack
            except:
                print "Error in pairing parantheses at ",i
                return None
            else:
                rite = i;
                node.set_range((left,rite))
                if len(stack) > 0:
                    (parent, left) = stack[-1]
                    parent.add_child(node)
                    if node.value in glob._attributes:
                        content = txt[node.ran[0]+1:node.ran[1]];
                        content = content.replace(node.value,'').split(',')
                        content = [item.strip() for item in content]
                        for att in content:
                            parent.add_attribute(node.value, att)
        else:
            continue;

    if len(stack) > 0:
        print "Error in pairing parantheses, left/right parantheses unbalanced."
        return None
    else:
        return tree



                    
