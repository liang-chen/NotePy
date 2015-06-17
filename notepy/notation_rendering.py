
from PIL import ImageFont, ImageDraw,Image
from mystruct import *
from font_dict import font_dict
import glob

def draw_stave(draw,left,rite):
    for i in range(-2,3):
        height = glob.center_height + i*glob.staff_gap #+ i*glob.staff_width
        draw.line((left, height, rite,height), width = glob.staff_width, fill=(0,0,0,0))

def draw_solid_prim(draw, font, prim, parms):
    i = parms[prim.locs[0][0][0]].value + prim.locs[0][0][1] + glob.solid_offset[prim.name][0]
    j = parms[prim.locs[0][1][0]].value + prim.locs[0][1][1] + glob.solid_offset[prim.name][1]
#    draw.line((parms[prim.locs[0][1][0]].value + prim.locs[0][1][1],parms[prim.locs[0][0][0]].value + prim.locs[0][0][1],parms[prim.locs[0][1][0]].value + prim.locs[0][1][1]+1,parms[prim.locs[0][0][0]].value + prim.locs[0][0][1]+1),width = 5, fill = (255,0,0,0))
    draw.text((j, i), font_dict[prim.name],font=font,fill=(0,0,0,0))

def draw_bar(draw,bar,parms):
    i1 = parms[bar.locs[0][0][0]].value + bar.locs[0][0][1] - glob.staff_width/4
    j = parms[bar.locs[0][1][0]].value + bar.locs[0][1][1]
    i2 = parms[bar.locs[1][0][0]].value + bar.locs[1][0][1] + glob.staff_width/2    
    draw.line((j,i1, j,i2), width = glob.bar_width, fill=(0,0,0,0))

def draw_stem(draw,stem,parms):
    i1 = parms[stem.locs[0][0][0]].value + stem.locs[0][0][1]
    j = parms[stem.locs[0][1][0]].value + stem.locs[0][1][1]
    i2 = parms[stem.locs[1][0][0]].value + stem.locs[1][0][1]
    draw.line((j,i1, j,i2), width = glob.stem_width, fill=(0,0,0,0))

def draw_beam(draw,beam,parms):
    i1 = parms[beam.locs[0][0][0]].value + beam.locs[0][0][1]
    j1 = parms[beam.locs[0][1][0]].value + beam.locs[0][1][1] - glob.stem_width/3
    i2 = parms[beam.locs[1][0][0]].value + beam.locs[1][0][1]
    j2 = parms[beam.locs[1][1][0]].value + beam.locs[1][1][1] + glob.stem_width/2
#    print beam.locs
#    print i1,j1,i2,j2
    draw.polygon([(j1,i1),(j2,i2),(j2,i2+glob.beam_width),(j1,i1+glob.beam_width)],fill = (0,0,0,0))
   # draw.line((j1,i1, j2,i2), width = glob.beam_width, fill=(0,0,0,0))
    
def draw_prim(draw, font, prim, parms):
    if prim.name in glob.solid_symbol:
        draw_solid_prim(draw, font, prim, parms)
    elif prim.name == "bar":
        draw_bar(draw,prim, parms)
    elif prim.name == "stem":
        draw_stem(draw,prim,parms)
    elif prim.name == "beam" or prim.name == "part_beam":
        draw_beam(draw,prim,parms)
    #else:
        #do nothing here

def render_panorama(graph):
    img_width = glob.img_width
    img_height = glob.img_height
    
    prim = graph.prims[-1]
    #print "bar locs", prim.name, prim.locs, prim.num
    #print graph.parms
    img_width = graph.parms[prim.locs[prim.num-1][1][0]].value + prim.locs[prim.num-1][1][1] + glob.rite_margin
    
#    print img_height,img_width
    im = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0)) 
    draw = ImageDraw.Draw(im) 
    # use a truetype font
    font = ImageFont.truetype("Bravura.otf", size = glob.font_size, encoding = "unic")
    
    draw_stave(draw, glob.left_margin, img_width - glob.rite_margin)
    
    for prim in graph.prims:
        draw_prim(draw, font, prim, graph.parms)
    
    im.save('example.jpg')
    #im.close()
