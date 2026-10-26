#!/usr/bin/env python3
"""Developer-only panel renderer. Requires Pillow; runtime uses bundled PNGs."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parents[1]/'assets'
OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
CYAN='#33ccff'; AMBER='#ffbf33'; BG='#0b1322'; WHITE='#f2f6ff'; MUTED='#a8b9d2'
PANELS={
 'question':('01 / PREDICT','Two places. One mountain barrier.',[
  ('LOOK AT THE TERRAIN','During the southwest monsoon, which side would usually receive more rain?'),
  ('A  /  CYAN RING','Western coastal side'),('B  /  AMBER RING','Inland, toward Pune'),
  ('YOUR TURN','Choose A or B, and explain why. The answer stays hidden until you respond.')]),
 'hint':('01 / A HINT','Follow the incoming air.',[
  ('START AT THE SEA','Moist southwest monsoon air approaches from the Arabian Sea.'),
  ('LOOK AT THE ARROW','What happens when that air meets the Western Ghats?'),
  ('TRY AGAIN','Which side is more likely to receive rain, and why?')]),
 'partial':('01 / EXPLAIN YOUR THINKING','A choice is the beginning.',[
  ('GO ONE STEP FURTHER','What happens to moist air as it moves toward and over the mountains?'),
  ('MAKE THE CONNECTION','Explain how that could change rainfall on either side.'),
  ('A / CYAN: COAST     B / AMBER: INLAND','Say your reasoning in your own words. No technical vocabulary needed.')]),
 'explain':('02 / REVEAL','The mountain changes the air.',[
  ('1  /  RISE AND COOL','Moist air is lifted over the Ghats. As it rises, it cools and can reach saturation.'),
  ('2  /  CLOUD AND RAIN','Condensation and precipitation favour the incoming, windward side: A.'),
  ('3  /  THE DRIER LEE','Air reaching the inland side has often lost moisture. Descending air can warm, too.'),
  ('A SEASONAL PATTERN','This helps explain the contrast toward Pune. It does not mean Pune never gets rain. Say next to try another landscape.')]),
 'transfer':('03 / APPLY IT ELSEWHERE','Same idea. A different direction.',[
  ('NORTHERN ANDES / AROUND 22 DEGREES SOUTH','In this example, moisture approaches from the continental interior to the EAST.'),
  ('A  /  CYAN RING','Western side, toward northern Chile'),
  ('B  /  AMBER RING','Eastern Andean foothills'),
  ('YOUR TURN','Which side faces the moist air and is favoured for rainfall? Explain the mountain process, not just a letter.')]),
 'transfer_hint':('03 / A TRANSFER HINT','Trace the path from the east.',[
  ('FIND WHERE THE AIR STARTS','The schematic arrow approaches the mountains from the eastern side.'),
  ('REUSE THE MECHANISM','Which slope makes the air climb first? What happens as it rises?'),
  ('A / CYAN: WEST     B / AMBER: EAST','Choose a side and explain why. This is northern Andes geography, not a live forecast.')]),
 'transfer_partial':('03 / EXPLAIN THE TRANSFER','What makes that side wetter?',[
  ('EXPLAIN THE CAUSE','Connect incoming moisture, rising air, cooling and rainfall.'),
  ('CHECK THE DIRECTION','The air approaches from the east in this northern Andes example.'),
  ('A / CYAN: WEST     B / AMBER: EAST','Your explanation matters more than remembering a letter.')]),
 'transfer_explain':('04 / CONNECT THE TWO','Windward is a relationship.',[
  ('NORTHERN ANDES: B / EAST','Moist air from the continental interior meets the eastern slopes first and rises.'),
  ('WESTERN RAIN SHADOW','The western Atacama side is much drier. Multiple processes shape desert climates.'),
  ('THE DIRECTION CAN CHANGE','A was the incoming side in Maharashtra; B is the incoming side here. Southern Patagonia has a different prevailing-wind pattern.'),
  ('READY TO RECAP?','Say next. We will distinguish what you explained yourself from what you explored with help.')]),
 'recap':('05 / TAKE IT WITH YOU','Read the landscape. Follow the air.',[
  ('LOOK FOR THE MOISTURE','Where is the air coming from?'),
  ('FIND THE BARRIER','Which slope makes the air rise and cool?'),
  ('EXPLAIN THE CONTRAST','Windward precipitation and leeward conditions can create a rain shadow.'),
  ('YOUR OWN LEARNING RECAP','Ask Nara what your answers demonstrated, what needed a hint, and what remains worth exploring.')])
}

def wrap(draw,text,font,width):
    words=text.split(); lines=[]; row=''
    for word in words:
        trial=(row+' '+word).strip()
        if draw.textlength(trial,font=font)>width and row:
            lines.append(row); row=word
        else: row=trial
    return lines+[row]

def render(name,data):
    step,title,rows=data
    im=Image.new('RGB',(1920,1080),BG); d=ImageDraw.Draw(im)
    d.rounded_rectangle((24,24,1896,1056),radius=30,outline='#263e5b',width=3)
    d.rectangle((60,64,70,160),fill=CYAN)
    d.text((100,64),'THE GLOBE IS YOUR CLASSROOM',font=ImageFont.truetype(BOLD,24),fill=MUTED)
    d.text((100,112),step,font=ImageFont.truetype(BOLD,24),fill=CYAN)
    y=186
    for ln in wrap(d,title,ImageFont.truetype(BOLD,55),1720):
        d.text((100,y),ln,font=ImageFont.truetype(BOLD,55),fill=WHITE); y+=70
    y+=24
    for label,body in rows:
        d.text((100,y),label,font=ImageFont.truetype(BOLD,24),fill=AMBER); y+=38
        body_size=36 if len(rows)==4 else 42
        for ln in wrap(d,body,ImageFont.truetype(FONT,body_size),1700):
            d.text((100,y),ln,font=ImageFont.truetype(FONT,body_size),fill=WHITE); y+=body_size+12
        y+=24
    if y>935: raise RuntimeError('Panel overflows: '+name+' '+str(y))
    source='Sources: NASA Earth Observatory / Met Office' if name.startswith('transfer') else 'Sources: NCERT / UNESCO / Government of Maharashtra / Met Office'
    if name=='recap': source='Sources and geographic scope: see SOURCES.md in the skill package'
    d.line((100,953,1820,953),fill='#263e5b',width=2)
    d.text((100,975),'Real Google Earth terrain. Rings and airflow are schematic; no live weather measurements.',font=ImageFont.truetype(FONT,22),fill=MUTED)
    d.text((100,1011),source,font=ImageFont.truetype(FONT,20),fill=MUTED)
    im.save(OUT/(name+'.png'))

for name,data in PANELS.items(): render(name,data)
im=Image.new('RGB',(1920,1080),BG); d=ImageDraw.Draw(im)
cx,cy,r=960,360,180
d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=CYAN,width=6)
d.ellipse((cx-r*.5,cy-r,cx+r*.5,cy+r),outline=CYAN,width=3)
for y in [cy-70,cy,cy+70]: d.line((cx-r+18,y,cx+r-18,y),fill=CYAN,width=3)
for y,text in [(610,'THE GLOBE IS'),(700,'YOUR CLASSROOM')]:
    f=ImageFont.truetype(BOLD,64); w=d.textlength(text,font=f); d.text(((1920-w)/2,y),text,font=f,fill=WHITE)
for y,text in [(825,'PREDICT  /  EXPLAIN  /  APPLY'),(950,'An interactive geography skill for Nara + Liquid Galaxy')]:
    f=ImageFont.truetype(FONT,29); w=d.textlength(text,font=f); d.text(((1920-w)/2,y),text,font=f,fill=MUTED)
im.save(OUT/'branding.png')
print('Built',len(PANELS)+1,'panels')
