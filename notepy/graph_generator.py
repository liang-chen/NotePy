
from mystruct import *
import glob
import operator
from operator import itemgetter
from itertools import *

def check_node(node):
    if not node.children and node.value in glob._attributes:
        return True
    else:
        result = True
        for child in node.children:
            if (node.value, child.value) not in glob._hierarchy:
                return False
            result = check_node(child)
        return result            

def check_tree(tree):
    if tree.root.value != "system":
        print "Error in parsing the syntax tree, root error: ",tree.root.value
        return False
    else:
        #check the hierachy
        result = True
        result = check_node(tree.root)
        return result
        
def add_bar(graph,bar,s,curj):
    i1 = glob.staff_top
    i2 = glob.staff_bot
    j = curj
    parm1 = Parm(i1, 'c')#top i, constant
    parm2 = Parm(i2, 'c')#bot i, constant
    parm3 = Parm(j, 'h')#can be set as constant later, horizontal
    graph.add_prim(bar)
    ind1 = graph.add_parm(parm1)
    ind2 = graph.add_parm(parm2)
    ind3 = graph.add_parm(parm3)
    bar.set_loc([[ind1, 0], [ind3, 0]],0)#top parm
    bar.set_loc([[ind2, 0], [ind3, 0]], 1)#bot parm
    bar.set_sym_index(s)
    return j+glob.inter_sym_dis

def add_solid_prim(graph,prim,s,curj,h,pt = ["c","h"]):
    i = h
    j = curj
    parm1 = Parm(i,pt[0])
    parm2 = Parm(j,pt[1])
    ind1 = graph.add_parm(parm1)
    ind2 = graph.add_parm(parm2)
    prim.set_loc([[ind1, 0], [ind2, 0]],0)#parm
    prim.set_sym_index(s)
    graph.add_prim(prim)
    return j+glob.inter_sym_dis

def add_ledger_prim(graph,prim,s,curj):
    ##loc has been set when connecting to its master notehead
    prim.set_sym_index(s)
    graph.add_prim(prim)
    return curj

def add_stem_prim(graph,stem,s,curj,up):
    if up:
        i1 = glob.center_height#top
    else:
        i1 = glob.center_height - glob.stem_len#top
    j = curj
    parm1 = Parm(i1,"v")#vertical
    parm2 = Parm(i1+glob.stem_len,"v")
    parm3 = Parm(j,"h")
    ind1 = graph.add_parm(parm1)
    ind2 = graph.add_parm(parm2)
    ind3 = graph.add_parm(parm3)
    stem.set_loc([[ind1, 0], [ind3, 0]],0)#top parm
    stem.set_loc([[ind2, 0], [ind3, 0]],1)#bot parm
    stem.set_sym_index(s)
    graph.add_prim(stem)
#    graph.add_edge(stem,stem,0,1,'v',glob.stem_len)#set stem to have flexible length
    return j

def add_beam_prim(graph,beam,s,curj):
    j1 = curj
    j2 = curj+glob.beam_len if beam.name == 'beam' else curj+glob.part_beam_len #just expected values
    i1 = glob.center_height
    i2 = i1
    parm1 = Parm(i1,"v")
    parm2 = Parm(i2,"v")
    parm3 = Parm(j1,"h")
    parm4 = Parm(j2,"h")
    ind1 = graph.add_parm(parm1)
    ind2 = graph.add_parm(parm2)
    ind3 = graph.add_parm(parm3)
    ind4 = graph.add_parm(parm4)
    beam.set_loc([[ind1, 0], [ind3, 0]],0)#left parm
    beam.set_loc([[ind2, 0], [ind4, 0]],1)#rite parm
    beam.set_sym_index(s)
    graph.add_prim(beam)
    return j2

def add_graph_prim_parm(graph,prim,s,curj,h = glob.center_height, up = 0):
    if prim.name == "bar":
        newj = add_bar(graph,prim,s,curj)
    elif prim.name in glob.solid_symbol:
        newj = add_solid_prim(graph,prim,s,curj,h)
    elif prim.name == "stem":
        newj = add_stem_prim(graph,prim,s,curj,up)
    elif prim.name == "beam" or prim.name == 'part_beam':
        newj = add_beam_prim(graph,prim,s,curj)
    elif prim.name == "ledger_line":
        newj = add_ledger_prim(graph,prim,s,curj)
    else:
        newj = curj + glob.inter_sym_dis
        #simply do nothing here
    return newj

def connect_prim_knots(primary, dependence, loc1, loc2, tp, shift):
    #share the parms of primary with dependence, index-based, not an efficient implementation, every update needs to consider other connected primitives
    if tp == 'h':
        loc_prim = primary.locs[loc1]
        loc_dep = dependence.locs[loc2]
        new_loc = [[loc_dep[0][0],loc_dep[0][1]],[loc_prim[1][0],loc_prim[1][1]]]
        new_loc[1][1] = new_loc[1][1] + shift
        dependence.set_loc(new_loc,loc2)
    elif tp == 'v':
        loc_prim = primary.locs[loc1]
        loc_dep = dependence.locs[loc2]
        new_loc = [[loc_prim[0][0],loc_prim[0][1]],[loc_dep[1][0],loc_dep[1][1]]]
        #print loc_dep," dependent locs ",new_loc
        new_loc[0][1] = new_loc[0][1] + shift
        #print "changed new loc ",new_loc
        dependence.set_loc(new_loc,loc2)
#    else:
#        print "Cannot find this kind of primitive knot!"

def update_related_prim_parms(prims, old_parm, new_parm):
    #not good to realize this way
    for prim in prims:
        for i in range(prim.num):
            if prim.locs[i][0][0] == old_parm:
                prim.locs[i][0][0] = new_parm
            elif prim.locs[i][1][0] == old_parm:
                prim.locs[i][1][0] = new_parm

def pairs(lst):
    i = iter(lst)
    first = prev = item = i.next()
    for item in i:
        yield prev, item
        prev = item

def add_clef_key(graph, clef_key,s,j,clef,keys):
    if clef_key.attribute['c'][0] == "treble":#needs to do data checking first
        #print "here is",clef.attribute['c']
        prim = Primitive("treble_clef",1,0)
        clef = "treble"
        newj = add_graph_prim_parm(graph,prim,s,j)
    elif clef_key.attribute['c'][0] == "bass":
        prim = Primitive("bass_clef",1,0)
        clef = "bass"
        newj = add_graph_prim_parm(graph,prim,s,j)
    else:
        newj = curj + glob.inter_sym_dis
        #simply do nothing here
    
    #time signature
    if 't' in clef_key.attribute.keys():
        num = clef_key.attribute['t'][0]
        time_top_prim = Primitive("time_"+str(num),1,0)
        newj = add_graph_prim_parm(graph,time_top_prim,s,j,h = glob.staff_top + glob.staff_gap)
        num = clef_key.attribute['t'][1]
        time_bot_prim = Primitive("time_"+str(num),1,0)
        newj = add_graph_prim_parm(graph,time_bot_prim,s,j, h = glob.staff_bot - glob.staff_gap)
        
        graph.add_edge(time_top_prim, time_bot_prim, 0 , 0, "h", 0)
        graph.add_edge(prim, time_top_prim, 0 , 0, "h", glob.inner_sym_dis)

    return newj

def get_acc(p,acc,clef,keys):
    #should be related to the key, currently just consider the plain explanation
    ad = {'sharp':0,
          'flat':0,
          'natural':0}
    if acc == 'none':
        return ad
    else:
        print "here is the original acc", acc
    for a in acc:
        if a == '#':
            ad['sharp'] = ad['sharp']+1
        elif a == 'b':
            ad['flat'] =ad['flat']+1
        elif a == 'n':
            ad['natural'] = ad['natural']+1
        else:
            raise Exception('Cannot handle this type of accidental: '+a)

    return ad

def find_pitch_height(pitch, clef, keys):#needs to parse the string into midi numbers
    p2i = glob.pitch_index
    i2p = glob.index_pitch
    ##p2i and i2p should be updated according to keys
    indices = p2i.values()
    indices.sort()

    p = pitch[0]
    
    diff = [abs(elem - p%12) for elem in indices]
    opti = diff.index(min(diff))
    optp = indices[opti]
    
    acc = get_acc(pitch[0],pitch[1],clef,keys) #type,num of accidentals

    ledger = 0
    
    ##only works for treble clef for now
    if clef == 'treble':
        pos_diff = (p - 60)/12#C4 for reference
        height = glob.center_height + 3*glob.staff_gap - pos_diff*(3.5*glob.staff_gap) - float(opti)*(0.5*glob.staff_gap)

        if height > glob.center_height + 2*glob.staff_gap or height < glob.center_height - 2*glob.staff_gap:
            ledger = 1
        
        return [height,acc,ledger]
    else:
        #simply do nothing
        return [glob.center_height,acc,ledger]

def get_acc_name(acc,num):
    if num > 2 or num < 0:
        error('Cannot handle '+str(num)+' accidentals.')
    if num == 1:
        return 'single_'+acc
    elif num == 2:
        return 'double_'+acc
    else:
        return 'none'
    
def add_acc(graph,note_head,acc,s,j,onset):
    for a in acc:
        if acc[a] == 0:
            continue
        name = get_acc_name(a,acc[a])
        print "acc name ",name, "from acc ",acc
        if name != 'none':#should have connection to adjacent accidentals
            prim = Primitive(name,1,onset)
            add_graph_prim_parm(graph,prim,s,j)
            connect_prim_knots(note_head,prim,0,0,'v',0)
            connect_prim_knots(note_head,prim,0,0,'h',-glob.note_head_to_sat)

def add_ledger_line(graph,note_head,s,j,onset):
    prim = Primitive("ledger_line", 1,onset)
    add_graph_prim_parm(graph,prim,s,j)
    connect_prim_knots(note_head,prim,0,0,'v',0)
    connect_prim_knots(note_head,prim,0,0,'h',0)
            
def add_note_head(graph,name,onset,pitch,s,j,clef,keys):
    """ generic function to add all sorts fo note heads and its satellites"""
    [height,acc,ledger] = find_pitch_height(pitch,clef,keys)
    prim = Primitive(name,1,onset)#prim is the primitive of notehead
    newj = add_graph_prim_parm(graph,prim,s,j,h = height)
    add_acc(graph,prim,acc,s,j,onset)
    if ledger:
        add_ledger_line(graph,prim,s,j,onset)
    return [height,prim,newj]

def add_whole_note(graph,whole,s,j,clef,keys):
    onset = whole.attribute['o'][0]#need to parse string into float numbers
    prev_note = None
    for pitch in whole.attribute['p']:
        [height,prim,newj] = add_note_head(graph,"whole_note_head",onset,pitch,s,j,clef,keys)
        #height = find_pitch_height(pitch,clef,keys)
        #prim = Primitive("whole_note_head",1,onset)#should align the noteheads vertically
        #newj = add_graph_prim_parm(graph,prim,s,j,h = height)
        if prev_note:
            #connect_prim_knots(prev_note,prim,0,0,'h',0)
            old_parm = prim.locs[0][1][0]
            connect_prim_knots(prev_note,prim,0,0,'h',0)
            new_parm = prim.locs[0][1][0]
            pps = [pp for pp in graph.prims if pp.symbol == prim.symbol]
            update_related_prim_parms(pps, old_parm, new_parm)
        prev_note = prim
    return newj

def add_half_note(graph,half,s,j,clef,keys):
    onset = half.attribute['o'][0]
    top_height = glob.img_height
    bot_height = 0
    prev_note = None

    aug_num = int((half.attribute['d'][0] - 1/2.0)*4)
    
    #for note head and its satellites
    for pitch in half.attribute['p']:
        [height,prim,newj] = add_note_head(graph,"open_note_head",onset,pitch,s,j,clef,keys)
        #height = find_pitch_height(pitch,clef,keys)
        #prim = Primitive("open_note_head",1,onset)
        #newj = add_graph_prim_parm(graph,prim,s,j,h = height)
        if height > bot_height:
            bot_note = prim
            bot_height = height
        if height < top_height:
            top_note = prim
            top_height = height
        if prev_note:
            #connect_prim_knots(prev_note,prim,0,0,'h',0)
            old_parm = prim.locs[0][1][0]
            connect_prim_knots(prev_note,prim,0,0,'h',0)
            new_parm = prim.locs[0][1][0]
            pps = [pp for pp in graph.prims if pp.symbol == prim.symbol]
            update_related_prim_parms(pps, old_parm, new_parm)
        prev_note = prim

        if aug_num ==  1:#should be able to handle other cases
            aug = Primitive("single_aug_dot",1,onset)
            add_graph_prim_parm(graph,aug,s,newj)
            connect_prim_knots(prim,aug,0,0,'v',0)
            connect_prim_knots(prim,aug,0,0,'h',glob.note_head_to_sat)
        
    #for stem
    stem_up = True if half.attribute['dir'][0] == 'up' else False
    stem = Primitive("stem",2,onset)
    add_graph_prim_parm(graph,stem,s,j,up = stem_up)
 
    shift = glob.note_head_to_stem if stem_up else -glob.note_head_to_stem
    root_note = bot_note if stem_up else top_note
    connect_prim_knots(root_note,stem,0,0,'h',shift)
    connect_prim_knots(root_note,stem,0,1,'h',shift)

    if stem_up:
        connect_prim_knots(bot_note,stem,0,1,'v',0)
        connect_prim_knots(top_note,stem,0,0,'v',-glob.stem_len)
    else:
        connect_prim_knots(top_note,stem,0,0,'v',0)
        connect_prim_knots(bot_note,stem,0,1,'v',glob.stem_len)

    return newj

def get_flag_num(note):#need to write in a more generic way such that any chord can use this function
    dur = note.attribute['d'][0]
    if dur >= 1/4.0:
        flag = 0
        aug = int((dur-1/4.0)*8)
    elif dur >= 1/8.0:
        flag = 1
        aug = int((dur-1/8.0)*16)
    elif dur >= 1/16.0:
        flag = 2
        aug = int((dur-1/16.0)*32)
    elif dur >= 1/32.0:
        flag = 3
        aug = int((dur-1/32.0)*64)
    elif dur >= 1/64.0:
        flag = 4
        aug = int((dur-1/64.0)*128)
    else:
        flag = 0
        aug = 0
        print "Cannot handle this many flags."
    return (flag,aug)

def make_flag_name(flag_num, stem_up):
    if flag_num == 1 and stem_up:#should handle other cases
        flag_name = 'single_flag_up'
    elif flag_num == 1 and not stem_up:
        flag_name = 'single_flag_down'
    elif flag_num == 2 and stem_up:
        flag_name = 'double_flag_up'
    elif flag_num == 2 and not stem_up:
        flag_name = 'double_flag_down'
    elif flag_num == 3 and stem_up:
        flag_name = 'triple_flag_up'
    elif flag_num == 3 and not stem_up:
        flag_name = 'triple_flag_down'
    else:
        flag_name = 'none'
    return flag_name

def add_short_note(graph,note,s,j,clef,keys):
    """ add isolated note """
    onset = note.attribute['o'][0]
    top_height = glob.img_height
    bot_height = 0
    prev_note = None
    (flag_num,aug_num) = get_flag_num(note)
    
    for pitch in note.attribute['p']:
        [height,prim,newj] = add_note_head(graph,"solid_note_head",onset,pitch,s,j,clef,keys)
        #height = find_pitch_height(pitch,clef,keys)
        #prim = Primitive("solid_note_head",1,onset)
        #newj = add_graph_prim_parm(graph,prim,s,j,h = height)
        if height > bot_height:
            bot_note = prim
            bot_height = height
        if height < top_height:
            top_note = prim
            top_height = height
        if prev_note:
            #connect_prim_knots(prev_note,prim,0,0,'h',0)
            old_parm = prim.locs[0][1][0]
            connect_prim_knots(prev_note,prim,0,0,'h',0)
            new_parm = prim.locs[0][1][0]
            pps = [pp for pp in graph.prims if pp.symbol == prim.symbol]
            update_related_prim_parms(pps, old_parm, new_parm)
        prev_note = prim

        if aug_num == 1:#should handle other cases
            aug = Primitive("single_aug_dot",1,onset)
            add_graph_prim_parm(graph,aug,s, newj)
            connect_prim_knots(prim,aug,0,0,'v',0)
            connect_prim_knots(prim,aug,0,0,'h',glob.note_head_to_sat)

    #for stem
    stem_up = True if note.attribute['dir'][0] == 'up' else False
    stem = Primitive("stem",2,onset)
    add_graph_prim_parm(graph,stem,s, j,up = stem_up)
        
    shift = glob.note_head_to_stem if stem_up else -glob.note_head_to_stem
    root_note = bot_note if stem_up else top_note
    connect_prim_knots(root_note,stem,0,0,'h',shift)
    connect_prim_knots(root_note,stem,0,1,'h',shift)

    if stem_up:
        connect_prim_knots(bot_note,stem,0,1,'v',0)
#        connect_prim_knots(top_note,stem,0,0,'v',-glob.stem_len)
        graph.add_edge(stem,top_note,0,0,'v',glob.stem_len)
    else:
        connect_prim_knots(top_note,stem,0,0,'v',0)
        graph.add_edge(bot_note,stem,0,1,'v',glob.stem_len)
#        connect_prim_knots(bot_note,stem,0,1,'v',glob.stem_len)

    #for flag(s)
    flag_name = make_flag_name(flag_num,stem_up)
    if flag_name != 'none':
        flag = Primitive(flag_name,1,onset)
        add_graph_prim_parm(graph,flag,s,j)
        if stem_up:
            connect_prim_knots(stem,flag,0,0,'h',0)
            connect_prim_knots(stem,flag,0,0,'v',0)
        else:
            connect_prim_knots(stem,flag,1,0,'h',0)
            connect_prim_knots(stem,flag,1,0,'v',0)

    return newj

def add_chord(graph,chord,s,j,clef,keys):
    start_ind = graph.num
    if chord.attribute['d'][0] == 1:#need to parse string into float numbers
        newj = add_whole_note(graph,chord,s,j,clef,keys)
    elif chord.attribute['d'][0] >= 1/2.0 and chord.attribute['d'][0]< 1:
        newj = add_half_note(graph,chord,s,j,clef,keys)
    else:
        newj = add_short_note(graph,chord,s,j,clef,keys)
    end_ind = graph.num
    #change the primitive indices here, does it matter??
    graph.prims[start_ind:end_ind] =  sorted(graph.prims[start_ind:end_ind], key = lambda x : graph.parms[x.locs[0][1][0]].value + x.locs[0][1][1] )
    return newj

def select_beam_type(chords,btp,dur_list):
    if min(dur_list) > 1:
        return
    else:
        indices = [ind for ind,d in enumerate(dur_list) if d <= 1]
        new_btp_item = []
        for k, g in groupby(enumerate(indices), lambda (i,x):i-x):
            clist = map(itemgetter(1),g)
            if len(clist) == 1:
                new_btp_item.append((clist[0],'part_beam'))
            else:
                new_btp_item.append(([clist[0],clist[-1]],'beam'))
        btp.append(new_btp_item)
        new_dur_list = [d*2 for d in dur_list]
        select_beam_type(chords,btp,new_dur_list)    

def add_beam_note(graph,note,s,j,clef,keys):
    """ add each stem in the beamed group """
    start_ind = graph.num
    onset = note.attribute['o'][0]
    top_height = glob.img_height
    bot_height = 0
    prev_note = None
    (flag_num,aug_num) = get_flag_num(note)

    for pitch in note.attribute['p']:
        [height,prim,newj] = add_note_head(graph,"solid_note_head",onset,pitch,s,j,clef,keys)
        #height = find_pitch_height(pitch,clef,keys)
        #prim = Primitive("solid_note_head",1,onset)
        #newj = add_graph_prim_parm(graph,prim,s,j,h = height)
        if height > bot_height:
            bot_note = prim
            bot_height = height
        if height < top_height:
            top_note = prim
            top_height = height
        if prev_note:
            old_parm = prim.locs[0][1][0]
            connect_prim_knots(prev_note,prim,0,0,'h',0)
            new_parm = prim.locs[0][1][0]
            pps = [pp for pp in graph.prims if pp.symbol == prim.symbol]
            update_related_prim_parms(pps, old_parm, new_parm)
        prev_note = prim
        
        if aug_num == 1:#should handle other cases
            aug = Primitive("single_aug_dot",1,onset)
            add_graph_prim_parm(graph,aug,s,newj)
            connect_prim_knots(prim,aug,0,0,'v',0)
            connect_prim_knots(prim,aug,0,0,'h',glob.note_head_to_sat)

    #for stem
    stem_up = True if note.attribute['dir'][0] == 'up' else False
    stem = Primitive("stem",2,onset)
    newj = add_graph_prim_parm(graph,stem,s,j,up = stem_up)
    
    shift = glob.note_head_to_stem if stem_up else -glob.note_head_to_stem
    root_note = bot_note if stem_up else top_note
    connect_prim_knots(root_note,stem,0,0,'h',shift)
    connect_prim_knots(root_note,stem,0,1,'h',shift)
    
    if stem_up:
        connect_prim_knots(bot_note,stem,0,1,'v',0)
       # connect_prim_knots(top_note,stem,0,0,'v',-glob.stem_len)
        graph.add_edge(stem,top_note,0,0,'v',glob.stem_len)
    else:
        connect_prim_knots(top_note,stem,0,0,'v',0)
        graph.add_edge(bot_note,stem,0,1,'v',glob.stem_len)
       # connect_prim_knots(bot_note,stem,0,1,'v',glob.stem_len)
    
    end_ind = graph.num

    #change the primitive index here, does it matter??
    graph.prims[start_ind:end_ind] =  sorted(graph.prims[start_ind:end_ind], key = lambda x : graph.parms[x.locs[0][1][0]].value + x.locs[0][1][1] )
    stem_ind = graph.prims.index(stem)
    return [stem_ind, stem_up, newj]

def add_beam_prims(graph,chords,s, j,clef,keys):
    newj = j
    #for chords
    #use index to connect adjecent chord primitives, needs to be improve?
    prev_prim_ind = -1
    chord_stem_ind = {}
    for i in range(len(chords)):
        chord = chords[i]
        [stem_ind, stem_up, newj] = add_beam_note(graph,chord,s, j,clef,keys)
        if prev_prim_ind >= 0:
            prev_prim = graph.prims[prev_prim_ind]
            next_prim = graph.prims[prev_prim_ind+1]
           # print "prev prim",prev_prim.name, "next prim", next_prim.name
            graph.add_edge(prev_prim, next_prim, prev_prim.num-1 , 0, "h", glob.inter_stem_dis)
        prev_prim_ind = graph.num - 1
        chord_stem_ind[i] = (stem_ind, stem_up)

    #for beams
    btp = []
    onsets = [chord.attribute['o'][0] for chord in chords]
    dur_list = [chord.attribute['d'][0]*8 for chord in chords]
    select_beam_type(chords,btp,dur_list)
    prev_beams = []
    beam_count = 0
    for btp_item in btp:
        new_prev = []
        for beam_parm in btp_item:
            beam = Primitive(beam_parm[1],2)#don't add onset to beam primitives
            newj = add_graph_prim_parm(graph,beam,s,j)
            chord_ind = beam_parm[0]
            if beam_parm[1] == 'beam':#for full beam                
                (stem_start, stem_up) = chord_stem_ind[chord_ind[0]]
                stem = graph.prims[stem_start]
                vert_loc = 0 if stem_up else 1
                connect_prim_knots(stem,beam,vert_loc,0,'h',0)
                if len(prev_beams) == 0:#main beam
                    connect_prim_knots(stem,beam,vert_loc,0,'v',0)
                    
                (stem_end, stem_up) = chord_stem_ind[chord_ind[1]]
                stem = graph.prims[stem_end]
                vert_loc = 0 if stem_up else 1
                connect_prim_knots(stem,beam,vert_loc,1,'h',0)
                if len(prev_beams) == 0:#main beam
                    connect_prim_knots(stem,beam,vert_loc,1,'v',0)
                    
                if len(prev_beams) == 0:#main beam, hook the beam and stems
                    main_beam = beam
                    for (stem_ind,stem_up) in chord_stem_ind.values():
                        if stem_ind == stem_start or stem_ind == stem_end:
                            continue
                        stem = graph.prims[stem_ind]
                        if stem_up:
                            parm = graph.parms[stem.locs[0][0][0]]#top i
                            parm.set_type('d')#change to dependent type
                            i1 = graph.parms[beam.locs[0][0][0]]
                            i2 = graph.parms[beam.locs[1][0][0]]
                            j1 = graph.parms[beam.locs[0][1][0]]
                            j2 = graph.parms[beam.locs[1][1][0]]
                            w = (i2.value-i1.value)/(j2.value-j1.value+0.0001)
                            parm.set_dependent([graph.parms[stem.locs[0][1][0]] , j1, i1],[w,-w,1.0])
                            graph.add_dep(stem,beam,'t')
                        else:
                            parm = graph.parms[stem.locs[1][0][0]]#bot i
                            parm.set_type('d')#change to dependent type
                            i1 = graph.parms[beam.locs[0][0][0]]
                            i2 = graph.parms[beam.locs[1][0][0]]
                            j1 = graph.parms[beam.locs[0][1][0]]
                            j2 = graph.parms[beam.locs[1][1][0]]
                            w = (i2.value-i1.value)/(j2.value-j1.value+0.0001)
                            parm.set_dependent([graph.parms[stem.locs[1][1][0]] , j1, i1],[w,-w,1.0])
                            graph.add_dep(stem,beam,'b')
                            
            else: #for partial beam
                (stem_ind, stem_up) = chord_stem_ind[chord_ind]
                stem = graph.prims[stem_ind]
                vert_loc = 0 if stem_up else 1
                connect_prim_knots(stem,beam,vert_loc,0,'h',-glob.part_beam_len)
               # connect_prim_knots(stem,beam,vert_loc,0,'v',0)
                connect_prim_knots(stem,beam,vert_loc,1,'h',0)
               # connect_prim_knots(stem,beam,vert_loc,1,'v',0)
            if beam_count > 0:#hook parallel beams
                dis = beam_count if stem_up else -beam_count
                parm = graph.parms[beam.locs[0][0][0]]#left i
                parm.set_type('d')#change to dependent type
                i1 = graph.parms[main_beam.locs[0][0][0]]
                i2 = graph.parms[main_beam.locs[1][0][0]]
                j1 = graph.parms[main_beam.locs[0][1][0]]
                j2 = graph.parms[main_beam.locs[1][1][0]]
                w = (i2.value-i1.value)/(j2.value-j1.value+0.0001)
                parm.set_dependent([graph.parms[beam.locs[0][1][0]] , j1, i1],[w,-w,1.0])
#                beam.locs[0][0][1] = dis#set offset

                parm = graph.parms[beam.locs[1][0][0]]#right i
                parm.set_type('d')#change to dependent type
                parm.set_dependent([graph.parms[beam.locs[1][1][0]] , j1, i1],[w,-w,1.0])
#                beam.locs[1][0][1] = dis#set offset
                                
                graph.add_dep(beam,main_beam,dis)
           # for prev in prev_beams:
            #    if stem_up:
             #       
              #      connect_prim_knots(prev,beam,0,0,'v',glob.inter_beam_dis)
               #     connect_prim_knots(prev,beam,1,1,'v',glob.inter_beam_dis)
               # else:
               #     connect_prim_knots(prev,beam,0,0,'v',-glob.inter_beam_dis)
               #     connect_prim_knots(prev,beam,1,1,'v',-glob.inter_beam_dis)
               # break #only needs to connect one previous beam
            new_prev.append(beam)
        prev_beams = new_prev
        beam_count = beam_count + 1
    return newj
    
def add_beam(graph,beam,s, j,clef,keys):
    chords = beam.children
    chords.sort(key = lambda x: x.attribute['o'][0]) #sort chords in order
    newj = add_beam_prims(graph,chords,s, j,clef,keys)
    return newj

def add_symbol_graph(graph,symbol,s,j,clef,keys):
    if symbol.value == "clef":
        newj = add_clef_key(graph, symbol,s, j,clef,keys)#needs to work on key sig's
    elif symbol.value == "chord":
        newj = add_chord(graph,symbol,s, j,clef,keys)
    elif symbol.value == "beam":
        newj = add_beam(graph,symbol,s, j,clef,keys)
    elif symbol.value in glob.solid_symbol:#isolated symbols
        #newj = add_iso_symbol(graph,symbol,j,clef,keys)
        newj = j
    else:
        #simply do nothing here
        newj = j
    return newj
        
def add_horizontal_edge(graph,vert_added):
    pl = [prim for prim in graph.prims if prim.onset >= 0]
    pl.sort(key=lambda x: x.onset)
    for pair in pairs(pl):#first on the left and second on the right
        #if pair[0].locs[pair[0].num-1][1][0] != pair[1].locs[0][1][0]:
        
        #print "hello",pair[0].name, pair[1].name
        
        if pair[0].symbol != pair[1].symbol and (pair[0].symbol, pair[1].symbol) not in vert_added:
            if pair[0].onset == pair[1].onset and any(va in pair[0].name for va in glob.vertically_alignable)\
                and any(va in pair[1].name for va in glob.vertically_alignable):
                continue
            graph.add_edge(pair[0], pair[1], pair[0].num-1 , 0, "h", glob.inter_sym_dis)
        elif (pair[0].symbol, pair[1].symbol) in vert_added:
            if pair[0].onset < pair[1].onset:
                graph.add_edge(pair[0], pair[1], pair[0].num-1 , 0, "h", glob.inter_stem_dis)
            
def add_vertical_edge(graph):
    pl = [prim for prim in graph.prims if prim.onset >= 0 and any(va in prim.name for va in glob.vertically_alignable)]
    vert_added = []
    for p in pl:
        pvl = [pv for pv in pl if p.onset == pv.onset and p.symbol != pv.symbol and p.name == pv.name]
        for pv in pvl:
            graph.add_edge(p,pv,0,0,"h",0)
            if (p.symbol,pv.symbol) not in vert_added:
                vert_added.append((p.symbol,pv.symbol))
            break

    for p in graph.prims:
        if p.name == 'stem':
            graph.add_edge(p,p,0,1,'v',glob.stem_len)#set stem to have flexible length 
    return vert_added

def add_symbol_edges(graph):
    vert_added = add_vertical_edge(graph)
    add_horizontal_edge(graph,vert_added)

def fix_prim_parm(parms,prim,loc,ij):
    index = prim.locs[loc][ij][0]
    parm = parms[index]
    tp = 'c'
    parm.set_type(tp)

#currently only in panorama mode, containing only one staff line
def tree_to_prim_graph(tree):
#    if not check_tree(tree):
#        return None
    graph = Graph()
    system = tree.root
    staff = system.children[0]
    curj = glob.left_margin
    sym_index = 0
    curbar = Primitive("bar",2,0)
    curj = add_graph_prim_parm(graph,curbar,sym_index,curj)#0 for current symbol index of the bar?
    fix_prim_parm(graph.parms,curbar,0,1)

    #for clef and keys
    clef = 'treble'#default one
    keys = 0#default one
    
    for mea in staff.children:
        for symbol in mea.children:
            #print symbol.value
            sym_index = sym_index + 1
            curj = add_symbol_graph(graph,symbol,sym_index,curj,clef,keys)
        #add bar
        sym_index = sym_index + 1
        curbar = Primitive("bar",2,100)#tempoarily set onset to unrealistic value
        add_graph_prim_parm(graph,curbar,sym_index,curj)
        sym_index = 0
        
        add_symbol_edges(graph)
    return graph
