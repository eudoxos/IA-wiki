#!/usr/bin/python3

from fpdf import FPDF
import textwrap
import string
import cairo
import tempfile
import codecs

# logging
import logging
import colorlog
handler=colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s: %(message)s'))
log=colorlog.getLogger('example')
log.addHandler(handler)
log.setLevel(logging.DEBUG)


# input files
corp_IA,corp_EN="Corpora_IA_Wiki_4000_IA_ENDOFPAGE.txt","Corpora_IA_Wiki_4000_EN_ENDOFPAGE.txt"
# output file
pdfOut='wiki-cheat.2.pdf'

# return string without non-printable characters
def printable(s): return ''.join([c for c in s if c in string.printable])
# read all lines from IA and EN corpora, excluding ENDOFPAGE lines (unused)
log.info(f'Reading {corp_IA}, {corp_EN}')
ll_IA,ll_EN=[[printable(l) for l in codecs.open(c,encoding='utf8').readlines() if 'ENDOFPAGE' not in l] for c in (corp_IA,corp_EN)]
log.info(f'IA, EN: {len(ll_IA)}, {len(ll_EN)} lines')
# output variables
linesPerPage=30
charsPerLine=65
# relative extra vertical space between apragraphs (1.0 is normal text line distance)
interPar=.8

# wrap IA lines to charsPerLine
ll_IA_wrap=[textwrap.wrap(l,charsPerLine) for l in ll_IA]

# directory for images (automatically deleted when finished)
imgDir=tempfile.TemporaryDirectory()
log.info(f'Temporary directory is {imgDir.name}')

def makePng(pageNo,lines):
    png=f'{imgDir.name}/page-{pageNo:03d}.png'
    # w_pic, h_pic = 1748,2480 # 300 dpi
    w_pic, h_pic = 874, 1240 # 150 dpi
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32, w_pic, h_pic)
    ct = cairo.Context (surface)
    ct.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ct.set_font_size (24)
    ct.rectangle (0, 0, w_pic, h_pic)
    ct.set_source_rgb (1.00, 1.00, 1.00)
    ct.fill()
    ct.set_source_rgb(0,0,0)
    y,dy=0,26 # start at 0, increment by 26 for each line
    for ll in lines:
        for l in ll:
            y+=dy
            ct.move_to(10,y)
            if y>h_pic-dy: raise RuntimeError(f'page {pageNo}: text out of page vertically (y={y}, ht={h_pic})')
            ct.show_text(l)
        y+=int(round((dy*interPar)))
    surface.write_to_png(png)
    return png

pdf = FPDF('P', 'mm', 'A5')

currPage=0 # current page
currWrapped=0 # wrapped lines on this page so far
currIaLines=[] # lines grouped by corpus lines
currEnLines=[]
line=0 # current corpus line to be printed
while True:
    # fit as many corpus lines on the page as possible
    while True:
        if line>=len(ll_IA_wrap): break
        ia=ll_IA_wrap[line] # IA corpus line wrapped to PDF lines
        if currWrapped+len(ia)>linesPerPage:
            # next corpus line would not fit, page is done
            if currWrapped==0: raise RuntimeError(f'corpus line {line}: wraps to {len(ia)} page lines (maximum is {linesPerPage})')
            break
        else:
            # add corpus line and continue
            currIaLines+=[ia]
            currEnLines+=[ll_EN[line]]
            currWrapped+=len(ia)+float(interPar) # add extra line for inter-paragraph skip
            line+=1
    if currWrapped==0: break # no lines, finishing
    log.info(f'page {currPage}: {len(currIaLines)} IA lines, {len(currEnLines)} corpus lines ({line-len(currEnLines)}..{line-1})')
    pdf.add_page()
    # create PNG with IA lines printed, insert it into the PDF
    png=makePng(currPage,currIaLines)
    pdf.image(png,x=0,y=0,w=148,h=210)
    # add EN text as text
    pdf.set_font('Arial','',.01)
    pdf.set_text_color(210,210,210)
    for i,en in enumerate(currEnLines):
        pdf.set_xy(10,10*i)
        pdf.cell(0,0,txt=en,ln=1)
    # move to the next page
    currPage+=1
    currIaLines,currEnLines=[],[]
    currWrapped=0
log.info(f'Finished, writing {pdfOut}')
pdf.output(pdfOut)


