
space_unit = 20
font_size = int(4*space_unit)
staff_gap = space_unit
staff_width = int(space_unit/10)
ledger_width = int(2.6*staff_width)
ledger_radius = int(0.9*space_unit)
bar_width = int(space_unit/4)
double_bar_width = 2*bar_width
stem_width = int(space_unit/5)
stem_len = 3*space_unit
beam_width = int(staff_gap/2)
beam_len = int(2*space_unit)
part_beam_len = int(space_unit/1.2)

_symbols = ['beam', 'chord', 'rest', 'bar', 'text', 'slur', 'crescendo', 'clef']#, 'key', 'time']
_positions = ['top', 'bot', 'left', 'rite']
_attributes = ['c', 't', 'k','p','d', 'o', 'dir', 'num'] + _positions
##############clef,time,key,pitch,duration,onset,direction,number,positions

_flags = ['system', 'staff', 'measure'] + _symbols + _attributes
_hierarchy = [('system','staff'), ('staff','measure'), ('measure', 'beam'), ('measure', 'beam'), ('measure', 'chord'), ('measure', 'clef'), ('beam', 'chord'), ('measure','rest')]  #, ('clef','key'), ('clef', 'time')

inter_sym_dis = 3*space_unit
inter_stem_dis = space_unit*1.5
inter_beam_dis = int(space_unit/1.5)
inner_sym_dis = space_unit*2.5

left_margin = 5*space_unit
rite_margin = 5*space_unit
top_margin = 8*space_unit
bot_margin = 8*space_unit
img_height = top_margin + bot_margin + 4*staff_gap
center_height = img_height/2
img_width = 0 #unset yet
staff_top = top_margin
staff_bot = staff_top + 4*staff_gap
staff_left = left_margin
staff_rite = 0 #unset yet


#for pitches
pitch_index = {
    'c':0,
    'd':2,
    'e':4,
    'f':5,
    'g':7,
    'a':9,
    'b':11,
}

index_pitch = {
    0:'c',
    2:'d',
    4:'e',
    5:'f',
    7:'g',
    9:'a',
    11:'b',
}

#for symbol offsets [i,j]
solid_offset = {
    "treble_clef":[staff_gap + int(-2*font_size),int(-font_size/2.5)],
    "whole_note_head":[int(-2*font_size),int(-font_size/5)],
    "open_note_head":[int(-2*font_size),int(-font_size/7)],
    "solid_note_head":[int(-2*font_size),int(-font_size/7)],
    "single_aug_dot":[int(-2*font_size),0],
    "double_aug_dot":[0,0],
    "single_flag_up":[int(-2*font_size),0],
    "single_flag_down":[int(-2*font_size),0],
    "double_flag_up":[int(-2*font_size),0],
    "double_flag_down":[int(-2*font_size),0],
    "triple_flag_up":[int(-2*font_size),int(-font_size/80)],
    "triple_flag_down":[int(-2*font_size),int(-font_size/80)],
    "single_sharp":[int(-2*font_size),int(-font_size/4)],
    "single_flat":[int(-2*font_size),int(-font_size/4)],
    "single_natural":[int(-2*font_size),int(-font_size/4)],
    "double_sharp":[int(-2*font_size),int(-font_size/4)],
    "double_flat":[int(-2*font_size),int(-font_size/4)],
    "double_natural":[int(-2*font_size),int(-font_size/4)],
    "time_0":[int(-2*font_size),int(-font_size/7)],
    "time_1":[int(-2*font_size),int(-font_size/7)],
    "time_2":[int(-2*font_size),int(-font_size/7)],
    "time_3":[int(-2*font_size),int(-font_size/7)],
    "time_4":[int(-2*font_size),int(-font_size/7)],
    "time_5":[int(-2*font_size),int(-font_size/7)],
    "time_6":[int(-2*font_size),int(-font_size/7)],
    "time_7":[int(-2*font_size),int(-font_size/7)],
    "time_8":[int(-2*font_size),int(-font_size/7)],
    "time_9":[int(-2*font_size),int(-font_size/7)]
}
solid_symbol = list(solid_offset.keys())

#for isolated symbol #do we need this?
#iso_symbol = {"rest", "text"}

#for prim-to-prim distance
note_head_to_stem = space_unit/1.9
note_head_to_sat = space_unit#/1.2

#for vertical alignment
vertically_alignable = ['note_head','stem','flag','aug','sharp','flat','natural']
