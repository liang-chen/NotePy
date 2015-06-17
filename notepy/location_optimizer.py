
from graph_generator import *
from mystruct import *
import numpy as np
import math

def objective_function(edges):
    """transform to graph edges to a quadratic objective function"""
    ##larger one
    x = [edge.prim2.locs[edge.loc2][1][0] if edge.tp == 'h' else edge.prim2.locs[edge.loc2][0][0] for edge in edges]
    ##smaller one
    y = [edge.prim1.locs[edge.loc1][1][0] if edge.tp == 'h' else edge.prim1.locs[edge.loc1][0][0] for edge in edges]
    ##constant
    c = [edge.prim2.locs[edge.loc2][1][1] - edge.prim1.locs[edge.loc1][1][1] - edge.ideal if edge.tp == 'h' else edge.prim2.locs[edge.loc2][0][1] - edge.prim1.locs[edge.loc1][0][1] - edge.ideal for edge in edges]

    obj = [(xe,ye,ce) for xe,ye,ce in zip(x,y,c)]
    return obj

def get_first_derivative(obj,pl,parms):
    dev = np.array(np.zeros(len(pl)))
    for term in obj:
        x = parms[term[0]].value
        y = parms[term[1]].value
        c = term[2]

        if x - y + c >= 0:
            a = 1
        else:
            a = 10
        if parms[term[0]].tp == 'h' or parms[term[0]].tp == 'v':
            i1 = pl.index(term[0])
            dev[i1] = dev[i1] + 2*a*(x-y+c)
        elif parms[term[0]].tp == 'd':
            deps = parms[term[0]].dependent
            for dep in deps:
                parm = dep[0]
                if parm.tp != 'h' and parm.tp != 'v':
                    continue
                weight = dep[1]
                i1 = pl.index(parms.index(parm))
                dev[i1] = dev[i1] + 2*a*weight*(x-y+c)
            
        if parms[term[1]].tp == 'h' or parms[term[1]].tp == 'v':
            i2 = pl.index(term[1])
            dev[i2] = dev[i2] - 2*a*(x-y+c)
        elif parms[term[1]].tp == 'd':
             deps = parms[term[1]].dependent
             for dep in deps:
                 parm = dep[0]
                 if parm.tp != 'h' and parm.tp != 'v':
                     continue
                 weight = dep[1]
                 i2 = pl.index(parms.index(parm))
                 dev[i2] = dev[i2] + 2*a*weight*(x-y+c)
    return dev

def get_hessian(obj,pl,parms):
    hessian = np.zeros([len(pl),len(pl)])
    for term in obj:
        x = parms[term[0]].value
        y = parms[term[1]].value
        c = term[2]
        ##a is the scalor for penalty
        if x - y + c >= 0:
            a = 1
        else:
            a = 10
        if parms[term[0]].tp == 'h' or parms[term[0]].tp == 'v':
            i1 = pl.index(term[0])
            hessian[i1][i1] = hessian[i1][i1] + 2*a
        else:
            i1 = -1
        if parms[term[1]].tp == 'h' or parms[term[1]].tp == 'v':
            i2 = pl.index(term[1])
            hessian[i2][i2] = hessian[i1][i1] + 2*a
        else:
            i2 = -1

        if i1 >= 0 and i2 >= 0:
            hessian[i1][i2] = hessian[i1][i2] - 2*a
            hessian[i2][i1] = hessian[i2][i1] - 2*a

    return hessian

def evaluate_obj(obj,parms):
    result = 0
    for term in obj:
        x = parms[term[0]].value
        y = parms[term[1]].value
        c = term[2]
        if x + y - c >= 0:
            a = 1
        else:
            a = 10
        result = result + a*((x - y + c)**2)
    return result

def new_updates(updates,alpha):
    new = [alpha * update for update in updates]
    return new

def evaluate_updated_obj(obj,pl,parms,updates,alpha):
    newup = new_updates(updates,alpha)
    result = 0
    for term in obj:
        x = parms[term[0]].value
        if parms[term[0]].tp == 'h' or parms[term[0]].tp == 'v':
            xu = newup[pl.index(term[0])]
            xn = x - xu            
        else:
            xn = x

        y = parms[term[1]].value
        if parms[term[1]].tp == 'h' or parms[term[1]].tp == 'v':
            yu = newup[pl.index(term[1])]
            yn = y - yu
        else:
            yn = y

        c = term[2]
        if x + y - c >= 0:
            a = 1
        else:
            a = 10
        result = result + a*((xn - yn + c)**2)
    return result
    
def line_search(obj,pl,parms,updates):
    alpha = 1.0
    f = evaluate_obj(obj,parms)
#    print "f ",f
#    print "updated ",evaluate_updated_obj(obj,pl,parms,updates,alpha)
    while True:
        newf = evaluate_updated_obj(obj,pl,parms,updates,alpha)
        if alpha < 1e-4 or newf < f:
            break
        alpha = alpha/2        
#    print "alpha ",alpha
    return alpha
        
def gradient_descent_iter(obj,pl,parms):
    #iterate 10 times, didn't check the convergence
    for it in range(500):
#        hessian = get_hessian(obj,pl,parms)
        dev = get_first_derivative(obj,pl,parms)
#        updates = np.linalg.solve(hessian, dev)
        updates = dev
        step_size = line_search(obj,pl,parms,updates)
#        print "hessian ",hessian
#        print "dev ",dev
#        print "updates ",updates
        for i in range(len(pl)):
            parms[pl[i]].value = parms[pl[i]].value - step_size*updates[i]

def dog_leg_iter(obj,pl,parms):
    delta = 20
    for it in range(400):
        hessian = get_hessian(obj,pl,parms)
        dev = get_first_derivative(obj,pl,parms)
        dev = np.matrix(dev).transpose()
        pu = -np.linalg.norm(dev)/float(dev.transpose()*hessian*dev)*dev
        pb = -np.linalg.solve(hessian,dev)
        nu = np.linalg.norm(pu)
        nb = np.linalg.norm(pb)
        print "nu nb",nu,nb
        if nu > delta:
            updates = delta/nu*pu
        elif nu <= delta and nb > delta:
            #solve quadratic function here
            a = np.linalg.norm(pb-pu)**2
            b = 2*float((pb-pu).transpose()*(2*pu-pb))
            c = np.linalg.norm(2*pu-pb)**2 - delta**2
            a = a/c
            b = b/c
            c = 1.0
            r = math.sqrt(b**2 - 4*a*c)
            tao = (-b + r)/(2*a)
            if tao > 2 or tao < 1:
                tao = (-b - r)/(2*a)
            print "tao ", tao
            updates = pu + (tao-1)*(pb-pu)
        else:
            updates = pb

        print "updates ",updates
        print "dev ",dev
        for i in range(len(pl)):
            parms[pl[i]].value = parms[pl[i]].value + updates.item((i,0))
            
def round_up_parms(parms):
    for parm in parms:
        parm.value = int(round(parm.value))

def update_dependent_prim_locs(graph):
    parms = graph.parms
    for dep in graph.dep:
        slave = dep[0]
        master = dep[1]
        tp = dep[2]
        i1 = parms[master.locs[0][0][0]].value
        i2 = parms[master.locs[1][0][0]].value
        j1 = parms[master.locs[0][1][0]].value
        j2 = parms[master.locs[1][1][0]].value
        w = (i2 - i1)/( j2 - j1 + 0.0001)
                                                        
        if tp == 't': #stem-beam-top
            parms[slave.locs[0][0][0]].update_weights([w,-w,1.0])
            slave.locs[0][0][1] = w*slave.locs[0][1][1] - w*master.locs[0][1][1] + master.locs[0][0][1]##set offset
        elif tp == 'b': #stem-beam-bottom
            parms[slave.locs[1][0][0]].update_weights([w,-w,1.0])
            slave.locs[1][0][1]= w*slave.locs[1][1][1] - w*master.locs[0][1][1] + master.locs[0][0][1]##set offset
        else:#beam-to-beam-parallel, using numbers
            num = tp
            parms[slave.locs[0][0][0]].update_weights([w,-w,1.0])
            parms[slave.locs[1][0][0]].update_weights([w,-w,1.0])
            slave.locs[0][0][1] = w*slave.locs[0][1][1] - w*master.locs[0][1][1] + master.locs[0][0][1] + num*glob.inter_beam_dis##set offset
            slave.locs[1][0][1]= w*slave.locs[1][1][1] - w*master.locs[0][1][1] + master.locs[0][0][1] + num*glob.inter_beam_dis##set offset 
#            print "master left:",parms[master.locs[0][0][0]].value,master.locs[0][0][1]
#            print "slave left:",parms[slave.locs[0][0][0]].value,slave.locs[0][0][1]
#            print "left value:",parms[slave.locs[0][0][0]].value + slave.locs[0][0][1]
    for parm in parms:
        if parm.tp == 'd':
            parm.update_value()

def new_gradient_descent_iter(graph,obj,pl,parms):
    iterations = 0
    while True:
        #        hessian = get_hessian(obj,pl,parms)
        dev = get_first_derivative(obj,pl,parms)
        #        updates = np.linalg.solve(hessian, dev)
        updates = dev
        step_size = line_search(obj,pl,parms,updates)
        #        print "hessian ",hessian
        #        print "dev ",dev
        #        print "updates ",updates
        old_value = [parms[p].value for p in pl]
        for i in range(len(pl)):
            parms[pl[i]].value = parms[pl[i]].value - step_size*updates[i]
        update_dependent_prim_locs(graph)
        new_value = [parms[p].value for p in pl]
        if sum([abs(v1 - v2) for (v1,v2) in zip(old_value,new_value)]) < 1e-1:
            break
        iterations = iterations + 1
        #else:
         #   print sum([abs(v1 - v2) for (v1,v2) in zip(old_value,new_value)])
        
def optimize_graph_parms(graph):
    """ optimize the graph parameters """
    edges = graph.edges
    parms = graph.parms
    ph = [edge.prim1.locs[edge.loc1][1][0] for edge in edges if edge.tp == 'h'] + [edge.prim2.locs[edge.loc2][1][0] for edge in edges if edge.tp == 'h']#horizontal ones
    pv = [edge.prim1.locs[edge.loc1][0][0] for edge in edges if edge.tp == 'v'] + [edge.prim2.locs[edge.loc2][0][0]  for edge in edges if edge.tp == 'v']#horizontal \ones
    pl = list(set(pv + ph))
    pl = [p for p in pl if parms[p].tp != 'c' and parms[p].tp != 'd']
    
    obj = objective_function(edges)
    print "obj ",obj
    print "pl ",pl
    print "edges ",[(edge.prim2.name, edge.prim1.name) for edge in edges]
    new_gradient_descent_iter(graph,obj,pl,parms)
#    update_dependent_prim_locs(graph)
#    dog_leg_iter(obj,pl,parms)
    round_up_parms(parms)
    
    
