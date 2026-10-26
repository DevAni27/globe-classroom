"""Shared presentation system. Geometry remains lesson-authored; no invented data."""
import math
from pathlib import Path
from functools import lru_cache
import classroom as c

INK='#0a111b'; CARD='#111e2c'; EDGE='#263447'; WHITE='#edf3f7'; MUTED='#a4b3c4'; FAINT='#74859a'
ACCENT='#6ee7d2'
PALETTE={'cyan':'#6bd8f4','amber':'#f2c66d','green':'#8cddb0','red':'#f18b91','violet':'#b9a0ef','white':'#edf3f7'}

@lru_cache(maxsize=64)
def font(size,bold=False):
    from PIL import ImageFont
    path=c.ROOT/'assets'/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')
    if not path.exists():path=c.ROOT/'assets/DejaVuSans.ttf'
    return ImageFont.truetype(str(path),size)

def lines(draw,text,size,width,bold=False):
    result=[]
    for paragraph in text.split('\n'):
        row=''
        for word in paragraph.split():
            if draw.textlength(word,font=font(size,bold))>width:
                raise ValueError('A panel word is too wide; shorten it before deployment')
            candidate=(row+' '+word).strip()
            if row and draw.textlength(candidate,font=font(size,bold))>width:result.append(row);row=word
            else:row=candidate
        if row:result.append(row)
    return result

def block(draw,text,box,size=40,minimum=26,color=WHITE,bold=False,gap=12):
    x,y,w,h=box
    while size>minimum:
        try:rows=lines(draw,text,size,w,bold)
        except ValueError:size-=2;continue
        if len(rows)*(size+gap)<=h:break
        size-=2
    rows=lines(draw,text,size,w,bold)
    if len(rows)*(size+gap)>h:raise ValueError('Panel content exceeds its layout; shorten the lesson text')
    for row in rows:
        draw.text((x,y),row,font=font(size,bold),fill=color);y+=size+gap
    return y

def short(draw,text,width,size=24):
    while draw.textlength(text,font=font(size))>width and len(text)>1:text=text[:-2]+'…'
    return text

def ring(doc,lon,lat,radius_km,color):
    # All rings are teaching highlights, not geographic boundaries.
    points=[];radius=radius_km/111
    for i in range(81):
        a=2*math.pi*i/80
        points.append((lon+radius*math.cos(a)/math.cos(math.radians(lat)),lat+radius*math.sin(a),0))
    c.line(doc,points,'c0201820',7)
    c.line(doc,points,color,3.5)

def arrow(doc,points,color,camera_range):
    c.line(doc,points,'b0201820',7,'relativeToGround')
    c.line(doc,points,color,3.5,'relativeToGround')
    x,y,z=points[-1];a,b,_=points[-2]
    scale=math.cos(math.radians(y));dx=(x-a)*scale;dy=y-b
    distance=math.hypot(dx,dy)
    if distance<1e-10:return
    # Small arrowhead independent of long authored shaft/continental extent.
    length=min(distance*.16,camera_range/1000*.014/111)
    ux,uy=dx/distance,dy/distance
    head=[(x+(-ux*length-uy*length*.38)/scale,y-uy*length+ux*length*.38,z),
          (x,y,z),(x+(-ux*length+uy*length*.38)/scale,y-uy*length-ux*length*.38,z)]
    c.line(doc,head,color,3.5,'relativeToGround')

def panel(plan,state,path,content,visible):
    from PIL import Image, ImageDraw
    label,title,body,instruction,_=content(plan,state);step=plan['steps'][state['index']];phase=state['phase']
    im=Image.new('RGB',(1920,1080),INK);d=ImageDraw.Draw(im)
    # Generous safe margin; no content placed in the attribution strip at bottom.
    d.text((88,42),'GLOBE CLASSROOM',font=font(25,True),fill=WHITE)
    d.text((88,80),'LIQUID GALAXY  /  NARA',font=font(18),fill=FAINT)
    stage='APPLY' if step['kind']=='transfer' else 'EXPLAIN' if phase in ('feedback','explain') else 'INVESTIGATE' if phase in ('hint','partial') else 'PREDICT'
    if phase=='recap':stage='RECAP'
    d.text((1480,47),'STOP %02d / %02d'%(state['index']+1,len(plan['steps'])),font=font(23),fill=MUTED)
    d.line((88,120,1832,120),fill=EDGE,width=2)
    # A quiet four-part track retains orientation without four competing cards.
    for i,name in enumerate(['PREDICT','INVESTIGATE','EXPLAIN','APPLY']):
        x=88+i*443;active=name==stage
        d.line((x,145,x+410,145),fill=ACCENT if active else EDGE,width=4 if active else 2)
        d.text((x,164),'%02d  %s'%(i+1,name),font=font(19,active),fill=ACCENT if active else FAINT)
    block(d,title,(88,220,1744,132),size=54,minimum=38,bold=True,gap=12)
    block(d,step['place']+'  ·  '+step['time_context'],(90,355,1730,65),size=23,minimum=20,color=MUTED,gap=7)
    d.text((90,439),label,font=font(19,True),fill=ACCENT)
    diagram=step['explanation'][state['beat_index']].get('diagram') if phase=='explain' and not state.get('turn_feedback') else None
    if diagram:
        block(d,body,(90,482,1030,274),size=41,minimum=26,gap=11)
        d.rounded_rectangle((1180,434,1832,772),radius=18,fill=CARD,outline=EDGE,width=1)
        d.text((1206,454),'SCHEMATIC RELATIONSHIP',font=font(17,True),fill=FAINT)
        n=len(diagram);spacing=264/n
        for i,value in enumerate(diagram):
            y=int(490+i*spacing)
            d.ellipse((1208,y+3,1240,y+35),fill='#203d43')
            d.text((1218,y+8),str(i+1),font=font(15,True),fill=ACCENT)
            block(d,value,(1264,y,540,int(spacing)-10),size=27,minimum=21,gap=6)
            if i<n-1:d.line((1224,y+39,1224,int(y+spacing)),fill='#3b655f',width=2)
    else:block(d,body,(90,482,1720,286),size=43,minimum=28,gap=13)
    # The single action has stronger contrast than metadata or sources.
    d.rounded_rectangle((88,794,1832,918),radius=16,fill='#142d35')
    d.rectangle((88,810,93,902),fill=ACCENT)
    d.text((115,808),'YOUR NEXT STEP  ·  REPLY IN NARA',font=font(18,True),fill=ACCENT)
    block(d,instruction,(115,843,1680,68),size=29,minimum=22,gap=7)
    # Full concept details stay in the legend; the globe has only quiet labels.
    shown=[f for f in step['features'] if visible(f,state)][:4]
    for i,f in enumerate(shown):
        x=90+(i%2)*880;y=936+(i//2)*29
        d.ellipse((x,y+6,x+8,y+14),fill=PALETTE[f['color']])
        d.text((x+18,y),short(d,f['label'],825,20),font=font(20),fill=MUTED)
    titles={v['id']:v['title'] for v in plan['sources']}
    meta='Sources: '+'; '.join(titles[v] for v in step['source_ids'])
    d.text((90,1000),short(d,meta,1720,18),font=font(18),fill=FAINT)
    d.text((90,1030),short(d,step['visual_note'],1720,17),font=font(17),fill=FAINT)
    im.save(path)

def branding(plan,state,path):
    from PIL import Image, ImageDraw
    im=Image.new('RGB',(1920,1080),INK);d=ImageDraw.Draw(im)
    d.text((120,70),'LIQUID GALAXY  /  NARA',font=font(23),fill=MUTED)
    cx,cy,r=960,360,128
    for ratio in [.33,.66,1]:d.ellipse((cx-r*ratio,cy-r,cx+r*ratio,cy+r),outline=ACCENT,width=2)
    for dy in [-62,0,62]:d.line((cx-110,cy+dy,cx+110,cy+dy),fill=ACCENT,width=2)
    d.text((960,560),'THE GLOBE IS',anchor='mt',font=font(62,True),fill=WHITE)
    d.text((960,648),'YOUR CLASSROOM',anchor='mt',font=font(62,True),fill=WHITE)
    d.line((740,770,1180,770),fill=EDGE,width=2)
    title=short(d,plan['title'],1600,32)
    d.text((960,815),title,anchor='mt',font=font(32),fill=ACCENT)
    d.text((960,900),'OBSERVE  ·  REASON  ·  APPLY',anchor='mt',font=font(22),fill=MUTED)
    d.text((960,968),'STOP %02d / %02d'%(state['index']+1,len(plan['steps'])),anchor='mt',font=font(20),fill=FAINT)
    im.save(path)
