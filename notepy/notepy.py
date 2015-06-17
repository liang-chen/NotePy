import sys
from parser import *
from graph_generator import *
from notation_rendering import *
from location_optimizer import optimize_graph_parms

def main():
    txt = read_file('example.txt')
    t = parse_content(txt)
    g = tree_to_prim_graph(t)
    optimize_graph_parms(g)
    render_panorama(g)

if __name__ == '__main__':
  main()
