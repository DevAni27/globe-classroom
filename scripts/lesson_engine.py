#!/usr/bin/env python3
"""Render researched, topic-independent lesson plans on LG. No AI API calls."""
import argparse
import base64
import copy
import json
import math
import os
from pathlib import Path
import re
import shutil
import shlex
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

import classroom as c
import visuals

LEGACY_STATE=c.STATE
c.STATE=c.HOME/'state/globe-classroom-live.json'
SCHEMA_VERSION=1
COLORS={name:'ff'+value[5:7]+value[3:5]+value[1:3] for name,value in visuals.PALETTE.items()}

def need(condition,message):
    if not condition: raise ValueError(message)

def text(value,label,maximum=600):
    need(isinstance(value,str) and 0<len(value.strip())<=maximum,label+' must be nonempty text, max '+str(maximum)+' characters')

def number(value,label,minimum,maximum):
    need(isinstance(value,(float,int)) and not isinstance(value,bool) and math.isfinite(value) and minimum<=value<=maximum,label+' is out of range')

def coord(p):
    need(isinstance(p,list) and len(p) in (2,3),'Coordinates must be [longitude, latitude, optional altitude]')
    number(p[0],'Longitude',-180,180); number(p[1],'Latitude',-89,89)
    if len(p)==3: number(p[2],'Altitude',0,300000)

def validate(plan):
    need(isinstance(plan,dict),'Plan must be a JSON object')
    need(plan.get('schema_version')==SCHEMA_VERSION,'schema_version must be 1')
    for key in ['topic','title','audience','learning_goal']: text(plan.get(key),key,200)
    sources=plan.get('sources'); need(isinstance(sources,list) and 2<=len(sources)<=15,'Use 2 to 15 researched sources')
    ids=set()
    for source in sources:
        need(isinstance(source,dict),'Source must be an object')
        for key in ['id','title','url','supports']: text(source.get(key),'source.'+key,600)
        need(source['id'] not in ids,'Duplicate source ID'); ids.add(source['id'])
        u=urlsplit(source['url']); need(u.scheme=='https' and bool(u.hostname),'Source must have an HTTPS URL')
    steps=plan.get('steps'); need(isinstance(steps,list) and 2<=len(steps)<=8,'Use 2 to 8 inquiry steps')
    seen=set()
    for i,step in enumerate(steps):
        need(isinstance(step,dict),'Step must be an object')
        sid=step.get('id'); need(isinstance(sid,str) and re.fullmatch('[a-z][a-z0-9-]{0,39}',sid),'Step id must be a short lowercase identifier')
        need(sid not in seen,'Duplicate step ID'); seen.add(sid)
        for key,limit in [('title',110),('place',120),('time_context',180),('question',430),('narration',650),('follow_up',350),('visual_note',250)]: text(step.get(key),sid+'.'+key,limit)
        need(step.get('kind') in ('prediction','transfer'),'kind must be prediction or transfer')
        evidence=step.get('source_ids'); need(isinstance(evidence,list) and len(evidence)>0 and all(s in ids for s in evidence),'Every step must cite known source_ids')
        camera=step.get('camera'); need(isinstance(camera,dict),'Camera must be an object')
        if 'allow_rotation' in camera: need(type(camera['allow_rotation']) is bool,'camera.allow_rotation must be true or false')
        for key,low,high in [('longitude',-180,180),('latitude',-89,89),('range',500,25000000),('tilt',0,80),('heading',-360,360)]: number(camera.get(key),sid+'.camera.'+key,low,high)
        hints=step.get('hints'); need(isinstance(hints,list) and 1<=len(hints)<=3,'Use 1 to 3 hints')
        for h in hints: text(h,sid+'.hint',350)
        rubric=step.get('rubric'); need(isinstance(rubric,dict),'Rubric must be an object')
        text(rubric.get('expected'),sid+'.rubric.expected',500)
        for key in ['reasoning','misconceptions']:
            values=rubric.get(key); need(isinstance(values,list) and 1<=len(values)<=6,'Rubric '+key+' must be a short list')
            for v in values: text(v,'rubric.'+key,300)
        beats=step.get('explanation'); need(isinstance(beats,list) and 2<=len(beats)<=4,'Use 2 to 4 explanation beats')
        for beat in beats:
            need(isinstance(beat,dict),'Explanation beat must be an object')
            text(beat.get('title'),'beat.title',100); text(beat.get('text'),'beat.text',500); text(beat.get('narration'),'beat.narration',700)
            if 'diagram' in beat:
                need(isinstance(beat['diagram'],list) and 2<=len(beat['diagram'])<=4,'diagram needs 2 to 4 short causal labels')
                for item in beat['diagram']: text(item,'diagram label',30)
        features=step.get('features'); need(isinstance(features,list) and 1<=len(features)<=35,'Use 1 to 35 geographical features per step')
        for f in features:
            need(isinstance(f,dict),'Feature must be an object')
            need(f.get('type') in ('point','line','arrow','polygon'),'Feature type must be point, line, arrow or polygon')
            text(f.get('label'),'feature.label',120)
            if 'map_label' in f: text(f['map_label'],'feature.map_label',24)
            need(f.get('color') in COLORS,'Unknown feature color')
            reveal=f.get('show','question'); need(reveal in ('question','hint','explain') or type(reveal) is int and 0<=reveal<len(beats),'show must be question, hint, explain or a zero-based explanation beat')
            if f['type']=='point':
                coord(f.get('coordinates'))
                number(f.get('radius_km',5),'radius_km',.1,300)
            else:
                coords=f.get('coordinates'); need(isinstance(coords,list) and 2<=len(coords)<=1000,'Line/polygon coordinates must be a list')
                for p in coords: coord(p)
                if f['type']=='polygon': need(len(coords)>=4 and coords[0]==coords[-1],'Polygon ring must be closed with at least four coordinates')
            need(f.get('geometry_kind') in ('schematic','location','sourced'),'Declare geometry_kind as schematic, location or sourced')
            if f['geometry_kind']=='sourced': need(f.get('source_id') in ids,'Sourced geometry requires a known source_id')
    need(steps[0]['kind']=='prediction','First step must be a prediction')
    need(any(s['kind']=='transfer' for s in steps[1:]),'Include a transfer question at a different location')
    return plan

def load_plan(path):
    p=Path(path).expanduser(); need(p.stat().st_size<=2_000_000,'Lesson JSON exceeds 2 MB')
    return validate(json.loads(p.read_text(encoding='utf-8')))

def active_step(plan,state): return plan['steps'][state['index']]

def visible(feature,state):
    show=feature.get('show','question'); phase=state['phase']
    if show=='question': return True
    if show=='hint': return phase in ('hint','explain','recap')
    if show=='explain': return phase in ('explain','recap')
    return phase in ('explain','recap') and state['beat_index']>=show

def geometry(step,state):
    root,doc=c.document(); label_count=0
    for f in step['features']:
        if not visible(f,state): continue
        color=COLORS[f['color']]
        if f['type']=='point':
            lon,lat=f['coordinates'][:2]
            radius=max(f.get('radius_km',5),step['camera']['range']/1000*.025)
            visuals.ring(doc,lon,lat,radius,color)
        else:
            pts=[tuple(p) if len(p)==3 else (p[0],p[1],0) for p in f['coordinates']]
            if f['type']=='arrow': visuals.arrow(doc,pts,color,step['camera']['range'])
            elif f['type']=='line':
                c.line(doc,pts,'99101820',6); c.line(doc,pts,color,2.5 if f['geometry_kind']=='schematic' else 3.5)
            else:
                pm=c.tag(doc,'Placemark'); style=c.tag(pm,'Style')
                line_style=c.tag(style,'LineStyle'); c.tag(line_style,'color',color); c.tag(line_style,'width',2)
                c.tag(c.tag(style,'PolyStyle'),'color','28'+color[2:])
                poly=c.tag(pm,'Polygon'); c.tag(poly,'tessellate',1); c.tag(poly,'altitudeMode','clampToGround')
                ring=c.tag(c.tag(poly,'outerBoundaryIs'),'LinearRing')
                c.tag(ring,'coordinates',' '.join('%s,%s,%s'%p for p in pts))
        # Motion/area labels belong to the legend, avoiding collisions on Earth.
        if f['type']!='point' or label_count>=4: continue
        label_count+=1
        # Labels refer to visible teaching features, never hidden answer geometry.
        coordinates=f['coordinates'] if f['type']=='point' else f['coordinates'][len(f['coordinates'])//2]
        pm=c.tag(doc,'Placemark'); c.tag(pm,'name',f.get('map_label',f['label'][:23]+'…' if len(f['label'])>24 else f['label']))
        style=c.tag(pm,'Style'); c.tag(c.tag(style,'IconStyle'),'scale',0)
        label=c.tag(style,'LabelStyle'); c.tag(label,'color',color); c.tag(label,'scale',0.75)
        point=c.tag(pm,'Point'); c.tag(point,'altitudeMode','clampToGround')
        c.tag(point,'coordinates',str(coordinates[0])+','+str(coordinates[1])+',0')
    return c.xml(root)

def view_xml(step,preserve_heading=False):
    root=ET.Element('LookAt')
    for key in ['longitude','latitude','heading','tilt','range']:
        value=step['camera'][key]
        if key=='heading' and not preserve_heading and not step['camera'].get('allow_rotation',False):value=0
        ET.SubElement(root,key).text=str(value)
    ET.SubElement(root,'altitude').text='0'; ET.SubElement(root,'altitudeMode').text='relativeToGround'
    result=ET.tostring(root,encoding='unicode'); ET.fromstring(result); return result

def validate_feedback(value):
    need(isinstance(value,dict),'Feedback must be a JSON object')
    for key,limit in [('learner_summary',140),('feedback',300),('next_question',200),('narration',1600)]:
        text(value.get(key),'feedback.'+key,limit)
    body='Your idea: '+value['learner_summary']+'\n\n'+value['feedback']
    need(len(body)<=470,'Shorten learner_summary and feedback to fit the panel')
    need(value['narration'].strip().endswith(value['next_question'].strip()),
         'Narration must end with the exact next_question shown on the panel')
    need('?' not in value['feedback'],'Put the single follow-up question in next_question, not feedback')
    prefix=value['narration'].strip()[:-len(value['next_question'].strip())]
    need('?' not in prefix,'Narration must contain only the one final follow-up question')
    return {key:value[key].strip() for key in ('learner_summary','feedback','next_question','narration')}

def feedback_content(state):
    f=validate_feedback(state['turn_feedback'])
    return ('LET’S BUILD ON YOUR ANSWER',None,
            'Your idea: '+f['learner_summary']+'\n\n'+f['feedback'],
            f['next_question'],f['narration'])

def next_instruction(plan,state):
    if state['phase']=='feedback': return 'Say next to open explanation 1: '+active_step(plan,state)['explanation'][0]['title']+'.'
    if state['phase']=='explain':
        if state['beat_index']+1<len(active_step(plan,state)['explanation']): return 'Say next for the next explanation scene.'
        if state['index']+1<len(plan['steps']): return 'Say next to apply the idea at '+plan['steps'][state['index']+1]['place']+'.'
        return 'Say next to view your lesson recap.'
    return None

def content(plan,state):
    step=active_step(plan,state); phase=state['phase']
    if state.get('turn_feedback'):
        label,_,body,question,voice=feedback_content(state)
        if phase=='feedback':
            voice=voice[:-len(question)].rstrip() if voice.endswith(question) else voice
            question=next_instruction(plan,state); voice=voice+' '+question
        return label,step['title'],body,question,voice
    if phase=='explain':
        beat=step['explanation'][state['beat_index']]
        label='EXPLAIN / %s OF %s'%(state['beat_index']+1,len(step['explanation']))
        instruction=next_instruction(plan,state)
        voice=re.sub(r'\s*Say next.*$','',beat['narration'],flags=re.I).strip()+' '+instruction
        return label,beat['title'],beat['text'],instruction,voice
    if phase=='hint':
        hint=step['hints'][state['hint_index']]
        return 'A HINT / THINK AGAIN',step['title'],hint,'Reply in Nara with your prediction and your reason.',hint+' '+step['question']
    if phase=='partial':
        return 'EXPLAIN YOUR THINKING',step['title'],step['question'],step['follow_up'],step['question']+' '+step['follow_up']
    if phase=='recap':
        attempts=[v for values in state['records'].values() for v in values]
        correct=sum(v['verdict']=='correct' for v in attempts)
        supported=sum(v['verdict'] in ('partial','unclear','incorrect') for v in attempts)
        revealed=sum(v['verdict']=='revealed' for v in attempts)
        body=plan['learning_goal']+'\n\nRecorded responses: '+str(correct)+' assessed correct; '+str(supported)+' needing follow-up; '+str(revealed)+' explanations requested. These are interaction records, not a learning score.'
        return 'RECAP / YOUR REASONING',plan['title'],body,'Ask Nara what your answers demonstrated and which connection needed support.', 'We explored '+plan['topic']+'. '+body+' Ask me to recap your reasoning from your actual responses.'
    label='TRANSFER / A NEW PLACE' if step['kind']=='transfer' else 'PREDICT / BEFORE WE EXPLAIN'
    return label,step['title'],step['question'],'Answer in the Nara chat on your computer. Explain why; there are no rig-screen buttons.',step['narration']

def panel(plan,state,path):
    try: visuals.panel(plan,state,path,content,visible)
    except ImportError: raise RuntimeError('Panels need Pillow. Run in Ubuntu: sudo apt install -y python3-pil')

def branding(plan,state,path):
    visuals.branding(plan,state,path)

def transition(state,plan,action,verdict=None,evidence='',feedback=None):
    s=copy.deepcopy(state); step=active_step(plan,s); phase=s['phase']
    had_feedback=bool(s.get('turn_feedback'))
    if feedback is not None:
        need(action=='assess','Turn feedback can only accompany assess')
        feedback=validate_feedback(feedback)
    if action in ('assess','hint','reveal','next'): s.pop('turn_feedback',None)
    need(not s.get('restored'),'Display restored. Start a new lesson first.')
    if action in ('assess','hint','reveal'): need(phase in ('question','hint','partial'),'No open question at this stage')
    if action=='assess':
        need(verdict in ('correct','partial','incorrect','unclear'),'A valid --verdict is required')
        need(bool(evidence.strip()),'Assessments require --evidence based on the learner\'s actual response')
        s['records'][step['id']].append({'verdict':verdict,'evidence':evidence[:600],**({'feedback':feedback} if feedback else {})})
        if feedback: s['turn_feedback']=feedback
        if verdict=='correct': s['phase']='feedback' if feedback else 'explain'; s['beat_index']=0
        elif verdict in ('partial','unclear'): s['phase']='partial'
        else: s['phase']='hint'
    elif action=='hint':
        if phase=='hint': s['hint_index']=min(s['hint_index']+1,len(step['hints'])-1)
        s['phase']='hint'
    elif action=='reveal':
        s['records'][step['id']].append({'verdict':'revealed','evidence':'Learner explicitly requested the explanation.'})
        s['phase']='explain'; s['beat_index']=0
    elif action=='next':
        need(phase in ('explain','feedback'),'Answer the open question, request a hint, or explicitly ask to reveal. Next cannot skip it.')
        if phase=='feedback' or (phase=='explain' and had_feedback):
            s['phase']='explain'; s['beat_index']=0
        elif s['beat_index']+1<len(step['explanation']): s['beat_index']+=1
        elif s['index']+1<len(plan['steps']):
            s['index']+=1; s['phase']='question'; s['hint_index']=0; s['beat_index']=0
        else: s['phase']='recap'
    s['stage']=active_step(plan,s)['id']+'-'+s['phase']
    return s

def narrate(message):
    # Local voice output only; no provider keys, subscription or network TTS call.
    if shutil.which('powershell.exe'):
        encoded=base64.b64encode(message.encode('utf-8')).decode('ascii')
        ps="Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $t=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('"+encoded+"')); $s.Speak($t)"
        cmd=['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(ps.encode('utf-16le')).decode('ascii')]
    elif shutil.which('espeak-ng'): cmd=['espeak-ng','-s','155',message]
    elif shutil.which('say'): cmd=['say',message]
    else:
        print('Voice unavailable: on WSL enable Windows interoperability, or install espeak-ng on Linux. Text/rig still work.'); return False
    try:
        p=subprocess.run(cmd,capture_output=True,timeout=100)
        if p.returncode: print('Local voice failed; the deployed visual lesson remains available.'); return False
        return True
    except (OSError,subprocess.TimeoutExpired):
        print('Local voice did not finish; continue using text.'); return False

def render(plan,state,dest):
    dest.mkdir(parents=True,exist_ok=True)
    (dest/'scene.kml').write_bytes(geometry(active_step(plan,state),state))
    (dest/'camera.xml').write_text(view_xml(active_step(plan,state)))
    panel(plan,state,dest/'panel.png')
    branding(plan,state,dest/'branding.png')
    (dest/'narration.txt').write_text(content(plan,state)[4])

def deploy(plan,state):
    stop_motion(state)
    with tempfile.TemporaryDirectory(prefix='classroom-lesson-') as d:
        folder=Path(d); render(plan,state,folder)
        c.deploy(state,scene_data=(folder/'scene.kml').read_bytes(),panel_path=folder/'panel.png',camera_xml=(folder/'camera.xml').read_text(),branding_path=folder/'branding.png')
    _,_,body,instruction,voice=content(plan,state)
    print('Teaching reply (same as local narration):\n'+voice+'\n\nOn-screen next step: '+instruction)
    if state.get('voice'): narrate(voice)

def context(plan,state):
    step=active_step(plan,state)
    return dict(plan=state['plan'],index=state['index'],phase=state['phase'],voice=state.get('voice',False),
                place=step['place'],question=step['question'],rubric=step['rubric'],
                current_content=content(plan,state),next_instruction=next_instruction(plan,state),
                records=state['records'].get(step['id'],[])[-3:])

GX='http://www.google.com/kml/ext/2.2'
ET.register_namespace('gx',GX)

def orbit_kml(step,name,duration=24):
    number(duration,'Orbit duration',12,40)
    root,doc=c.document();tour=ET.SubElement(doc,'{'+GX+'}Tour');c.tag(tour,'name',name)
    playlist=ET.SubElement(tour,'{'+GX+'}Playlist')
    for n in range(13):
        fly=ET.SubElement(playlist,'{'+GX+'}FlyTo')
        ET.SubElement(fly,'{'+GX+'}duration').text=str(2 if n==0 else duration/12)
        ET.SubElement(fly,'{'+GX+'}flyToMode').text='smooth'
        view=copy.deepcopy(step)
        view['camera']['heading']=(step['camera']['heading']+n*30)%360
        view['camera']['tilt']=max(35,min(55,step['camera']['tilt']))
        look=ET.fromstring(view_xml(view,preserve_heading=True))
        for element in look.iter(): element.tag='{'+c.K+'}'+element.tag
        fly.append(look)
    fly=ET.SubElement(playlist,'{'+GX+'}FlyTo');ET.SubElement(fly,'{'+GX+'}duration').text='2'
    ET.SubElement(fly,'{'+GX+'}flyToMode').text='smooth'
    look=ET.fromstring(view_xml(step))
    for element in look.iter():element.tag='{'+c.K+'}'+element.tag
    fly.append(look)
    return c.xml(root)

def stop_motion(state,rig=None):
    motion=state.get('motion')
    if not motion:return
    rig=rig or c.Rig(c.connection())
    rig.ssh("printf '%s\\n' 'exittour=true' > /tmp/query.txt; sleep 1")
    # Remove only our exact one-shot tour link; preserve other applications' content.
    code="from pathlib import Path; p=Path('/var/www/html/kmls.txt'); u="+repr(motion['url'])+"; p.write_text('\\n'.join(v for v in p.read_text().splitlines() if v.strip()!=u)+'\\n')"
    rig.ssh('python3 -c '+shlex.quote(code))
    state.pop('motion',None);c.save_state(state)

def camera_action(plan,state,action):
    need(not state.get('restored'),'Start a lesson before controlling its camera')
    rig=c.Rig(c.connection());stop_motion(state,rig)
    if action=='orbit':
        token=str(time.time_ns());name='ClassroomOrbit'+token;filename='orbit-'+token+'.kml'
        url=c.URL+'/'+filename
        with tempfile.TemporaryDirectory(prefix='classroom-orbit-') as folder:
            p=Path(folder)/filename;p.write_bytes(orbit_kml(active_step(plan,state),name));rig.copy([p])
        # Persist before starting so stop remains available after an interrupted invocation.
        state['motion']=dict(url=url,name=name,expires_at=time.time()+35);c.save_state(state)
        rig.ssh("printf '%s\\n' "+shlex.quote(url)+" >> /var/www/html/kmls.txt; sleep 4; printf '%s\\n' "+shlex.quote('playtour='+name)+" > /tmp/query.txt")
        print('Requested one bounded orbit (about 28 seconds), ending at the lesson view. Confirm movement visually. Say stop moving to interrupt. Lesson progress unchanged.')
    elif action=='return-view':
        rig.ssh("printf '%s\\n' "+shlex.quote('flytoview='+view_xml(active_step(plan,state)))+" > /tmp/query.txt")
        print('Requested the saved lesson view; progress unchanged.')
    else:print('Stopped the classroom camera tour, if active. Lesson progress unchanged.')

def initial(plan,path,voice=False):
    return {'version':2,'plan':str(path),'index':0,'phase':'question','hint_index':0,'beat_index':0,'stage':plan['steps'][0]['id']+'-question','voice':voice,'records':{s['id']:[] for s in plan['steps']}}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['check','validate','start','status','assess','hint','reveal','next','continue','restore','speak','render','context','orbit','stop','return-view','end','clear'])
    ap.add_argument('--plan',type=Path); ap.add_argument('--verdict',choices=['correct','partial','incorrect','unclear'])
    ap.add_argument('--feedback-json',type=Path,help='Personalised learner feedback and matching narration JSON for assess')
    ap.add_argument('--evidence',default=''); ap.add_argument('--voice',action='store_true',help='Enable optional local narration; on WSL uses Windows installed speech voice')
    ap.add_argument('--output',type=Path,default=Path('/tmp/globe-classroom-preview'))
    a=ap.parse_args()
    feedback=None
    if a.feedback_json:
        need(a.action=='assess','--feedback-json requires assess')
        need(a.feedback_json.stat().st_size<=16000,'Feedback JSON exceeds 16 KB')
        feedback=validate_feedback(json.loads(a.feedback_json.read_text(encoding='utf-8')))
    if a.action=='check':
        import importlib.util
        print('Pillow:',bool(importlib.util.find_spec('PIL')))
        print('SSH:',bool(shutil.which('ssh')),'sshpass:',bool(shutil.which('sshpass')))
        print('Local voice:',bool(shutil.which('powershell.exe') or shutil.which('espeak-ng') or shutil.which('say')))
        print('Connection profile present:',(c.HOME/'state/lg-connection.json').exists()); return
    if a.action in ('validate','start','render'):
        if not a.plan: ap.error('--plan is required')
        plan=load_plan(a.plan)
        if a.action=='validate':
            print('Structure valid:',plan['title'],'/',len(plan['steps']),'steps. Source claims require factual review by Nara or a person.'); return
        if a.action=='render': render(plan,initial(plan,a.plan),a.output); print('Preview files:',a.output); return
        folder=c.HOME/'lessons'; folder.mkdir(parents=True,exist_ok=True)
        path=folder/('lesson-'+str(time.time_ns())+'.json'); path.write_text(json.dumps(plan,indent=2,ensure_ascii=False))
        state=initial(plan,path,a.voice)
        for oldpath in (c.STATE,LEGACY_STATE):
            if oldpath.exists():
                old=json.loads(oldpath.read_text())
                stop_motion(old)
                if old.get('backup') and not old.get('restored'):
                    for key in ('backup','backup_files'): state[key]=old[key]
                    break
        deploy(plan,state); return
    state=c.read_state()
    if a.action=='status':
        print(json.dumps(state,indent=2)); return
    if a.action in ('restore','end','clear'): stop_motion(state); c.restore(state); return
    plan=load_plan(state['plan'])
    if a.action=='context': print(json.dumps(context(plan,state),ensure_ascii=False,indent=2)); return
    if a.action in ('orbit','stop','return-view'): camera_action(plan,state,a.action); return
    if a.action=='speak': narrate(content(plan,state)[4]); return
    if a.action in ('assess','hint','reveal','next'): state=transition(state,plan,a.action,a.verdict,a.evidence,feedback)
    if a.action=='continue' and state.get('restored'): raise RuntimeError('Lesson has been restored. Use start for a new session.')
    deploy(plan,state)

if __name__=='__main__':
    try: main()
    except (RuntimeError,ValueError,OSError,KeyError,TypeError,subprocess.TimeoutExpired) as e:
        print('Classroom error: '+str(e),file=sys.stderr); sys.exit(1)
