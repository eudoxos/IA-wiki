#!/usr/bin/python

from fpdf import FPDF
import textwrap
import string
import cairo

file1 = "Corpora_IA_Wiki_4000_IA.txt"
file2 = "Corpora_IA_Wiki_4000_EN.txt"

def flatten (t):
  return [item for sublist in t for item in sublist]

def create_surface (filename):
  # w_pic, h_pic = 1748,2480 # 300 dpi
  w_pic, h_pic = 874, 1240 # 150 dpi
  if filename.endswith (".png"):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w_pic, h_pic)
  if filename.endswith (".pdf"):
    surface = cairo.PDFSurface (filename, w_pic, h_pic)
  ct = cairo.Context (surface)
  ct.select_font_face (
    "Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
  ct.set_font_size (24)
  ct.rectangle (0, 0, w_pic, h_pic)
  ct.set_source_rgb (1.00, 1.00, 1.00)
  ct.fill()
  return ct,surface

printable = set (string.printable)

def modify (text):
  result = []
  for ln in text:
    ln1 = ln.strip()
    ln1 = ''.join (filter (lambda x: x in printable, ln1))
    ln1 = textwrap.wrap (ln1, 65)
    result.extend (ln1)
  return result

import codecs
f1=codecs.open (file1,encoding='utf8')
f2 = codecs.open (file2,encoding='utf-8')


ttext1 = f1.readlines ()
#f.close ()


ttext2 = f2.readlines ()
#f.close ()

#ttext1 = modify (ttext1)
#ttext2 = modify (ttext2)


print(f'Text lengths: {len(ttext1)} {len(ttext2)}')
#text1 = text1 [:45]
#text2 = text2 [:45]

def printableOnly(t):
    return ''.join([c for c in t if c in string.printable])

pdf = FPDF('P', 'mm', 'A5')
pg=0
perPage=15
while True:
    # if pg>20: break
    i0,i1=pg*perPage,(pg+1)*perPage
    print(f'Page {pg}, {i0}...{i1}')
    if i0>=len(ttext1) or i1>=len(ttext2): break
    text1,text2=ttext1[i0:i1],ttext2[i0:i1]
    imgname = f"temp/pg{pg}.png"
    ct, surface = create_surface (imgname)
    ct.set_source_rgb (0.00, 0.00, 0.00)
    i=0
    for t1 in text1:
      tt=textwrap.wrap(t1,65)
      for t in tt: 
        ct.move_to (10,26*(i+1))
        # ct.show_text(''.join([c for c in t if c in string.printable]))
        ct.show_text(t)
        i+=1
    if imgname.endswith (".png"):
      surface.write_to_png (imgname)
    pdf.add_page ()
    pdf.image (imgname, x=0, y=0, w=148, h=210)
    pdf.set_font ('Arial', '', 0.01)
    pdf.set_text_color (210,210,210)
    pdf.set_xy (0,0)
    for i,t in enumerate (text2):
      pdf.cell (0,0,txt=printableOnly(t),ln=1)
    pg+=1


pdf.output ('wiki-cheat.pdf', 'F')

# print (text1)
# print (text2)

