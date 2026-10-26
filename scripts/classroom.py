#!/usr/bin/env python3
"""Globe Classroom: deterministic LG scenes, persistent lesson state, no AI SDK."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

K = 'http://www.opengis.net/kml/2.2'
ET.register_namespace('', K)
ROOT = Path(__file__).resolve().parents[1]
HOME = Path(os.environ.get('HERMES_HOME', Path.home()/'.hermes/profiles/liquid-galaxy-agent')).expanduser()
STATE = HOME/'state/globe-classroom.json'
REMOTE = '/var/www/html/kml/globe-classroom'
URL = 'http://lg1:81/kml/globe-classroom'
STAGES = ('question', 'hint', 'partial', 'explain', 'transfer', 'transfer_hint', 'transfer_partial', 'transfer_explain', 'recap')

def tag(parent, name, text=None, **attrs):
    e = ET.SubElement(parent, '{%s}%s' % (K,name), attrs)
    if text is not None:
        e.text = str(text)
    return e

def document():
    root = ET.Element('{%s}kml' % K)
    return root, tag(root,'Document')

def xml(root):
    data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    ET.fromstring(data)
    return data

def camera(stage):
    andes = stage.startswith('transfer') or stage == 'recap'
    lon, lat, distance = (-68.1,-22.0,1050000) if andes else (73.25,18.65,310000)
    e = ET.Element('LookAt')
    for key,value in [('longitude',lon),('latitude',lat),('altitude',0),('heading',0),('tilt',45),('range',distance),('altitudeMode','relativeToGround')]:
        ET.SubElement(e,key).text = str(value)
    return ET.tostring(e,encoding='unicode')

def line(doc, points, color, width=7, mode='clampToGround'):
    p = tag(doc,'Placemark')
    style = tag(p,'Style')
    ls = tag(style,'LineStyle')
    tag(ls,'color',color); tag(ls,'width',width)
    geom = tag(p,'LineString')
    tag(geom,'altitudeMode',mode)
    if mode == 'clampToGround': tag(geom,'tessellate',1)
    tag(geom,'coordinates',' '.join('%s,%s,%s' % xyz for xyz in points))

def circle(doc, lon,lat,radius,color):
    pts=[]
    for i in range(65):
        a=2*math.pi*i/64
        pts.append((lon+radius*math.cos(a)/math.cos(math.radians(lat)),lat+radius*math.sin(a),0))
    line(doc,pts,color,9)

def arrow(doc, points,color):
    line(doc,points,color,9,'relativeToGround')
    x,y,z=points[-1]; a,b,_=points[-2]
    dx,dy=x-a,y-b
    # Schematic arrowheads: geometric teaching aids, not measured wind vectors.
    line(doc,[(x-dx*.3-dy*.18,y-dy*.3+dx*.18,z),(x,y,z),(x-dx*.3+dy*.18,y-dy*.3-dx*.18,z)],color,9,'relativeToGround')

def scene(stage):
    root,doc=document()
    andes=stage.startswith('transfer') or stage=='recap'
    if andes:
        circle(doc,-70.0,-22.0,.13,'ffffcc33')
        circle(doc,-64.8,-22.0,.13,'ff33bfff')
        if stage not in ('transfer','transfer_partial'):
            arrow(doc,[(-63.5,-22,4500),(-65,-22,4500),(-66.5,-22,6500)],'ffffcc33')
        if stage in ('transfer_explain','recap'):
            arrow(doc,[(-66.5,-22,6500),(-68,-22,7500),(-70,-22,3000)],'ff33bfff')
    else:
        circle(doc,72.93,18.65,.035,'ffffcc33')
        circle(doc,73.86,18.52,.035,'ff33bfff')
        if stage in ('hint','explain'):
            arrow(doc,[(72.5,18.4,1700),(72.9,18.55,2000),(73.35,18.65,4300)],'ffffcc33')
        if stage=='explain':
            arrow(doc,[(73.35,18.65,4300),(73.55,18.6,3500),(74.0,18.5,1500)],'ff33bfff')
    return xml(root)

def overlay(image_url):
    root,doc=document()
    o=tag(doc,'ScreenOverlay'); tag(o,'name','Globe Classroom panel'); tag(o,'drawOrder',1000)
    tag(tag(o,'Icon'),'href',image_url)
    tag(o,'overlayXY',x='0.5',y='0.5',xunits='fraction',yunits='fraction')
    tag(o,'screenXY',x='0.5',y='0.5',xunits='fraction',yunits='fraction')
    # Zero height preserves the image aspect ratio; avoids stretching in VM windows.
    tag(o,'size',x='0.90',y='0',xunits='fraction',yunits='fraction')
    return xml(root)

def networklink():
    root,doc=document(); n=tag(doc,'NetworkLink')
    tag(n,'name','Globe Classroom: automatic scene updates')
    link=tag(n,'Link'); tag(link,'href',URL+'/scene.kml')
    tag(link,'refreshMode','onInterval'); tag(link,'refreshInterval',2)
    return xml(root)

def read_state():
    if not STATE.exists(): raise RuntimeError('No lesson started. Run: classroom.py start')
    return json.loads(STATE.read_text())

def save_state(s):
    STATE.parent.mkdir(parents=True,exist_ok=True)
    temp=STATE.with_suffix('.tmp'); temp.write_text(json.dumps(s,indent=2)+'\n')
    os.chmod(temp,0o600); temp.replace(STATE)

def connection():
    path=HOME/'state/lg-connection.json'
    if not path.exists(): raise RuntimeError('Nara connection profile is missing. Complete LG onboarding first.')
    d=json.loads(path.read_text())
    machine=''
    for p in ['/etc/machine-id','/var/lib/dbus/machine-id']:
        if Path(p).exists() and Path(p).read_text().strip():
            machine=Path(p).read_text().strip(); break
    import socket
    fp=hashlib.sha256('|'.join([machine,socket.gethostname(),str(Path.home().resolve())]).encode()).hexdigest()
    if not d.get('verified') or d.get('machine_fingerprint')!=fp:
        raise RuntimeError('Connection profile is not verified for this computer. Run Nara onboarding.')
    if not isinstance(d.get('screens'),int) or d['screens']<3 or d['screens']%2==0:
        raise RuntimeError('This version supports the standard odd LG layout with 3, 5, 7... screens.')
    if not shutil.which('sshpass'): raise RuntimeError('sshpass is missing. Install it in Ubuntu WSL.')
    return d

class Rig:
    def __init__(self,d):
        self.d=d
        self.env=dict(os.environ,SSHPASS=d['password'])
        self.options=['-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10']
        self.target='%s@%s'%(d['username'],d['ip'])
    def ssh(self,command,data=None):
        cmd=['sshpass','-e','ssh',*self.options,'-p',str(self.d['port']),self.target,command]
        p=subprocess.run(cmd,input=data,capture_output=True,env=self.env,timeout=30)
        if p.returncode:
            detail=p.stderr.decode(errors='replace').replace(self.d['password'],'[redacted]')
            raise RuntimeError('SSH failed: '+detail[-1500:])
        return p.stdout.decode().strip()
    def copy(self,paths):
        cmd=['sshpass','-e','scp','-O',*self.options,'-P',str(self.d['port']),*[str(p) for p in paths],self.target+':'+REMOTE+'/']
        p=subprocess.run(cmd,capture_output=True,env=self.env,timeout=45)
        if p.returncode:
            detail=p.stderr.decode(errors='replace').replace(self.d['password'],'[redacted]')
            raise RuntimeError('SCP failed: '+detail[-1500:])

def prepare_backup(rig,s):
    if s.get('backup'): return
    # Persist the backup location before mutation so an interrupted deploy is recoverable.
    backup='/home/%s/globe-classroom-backup-%s'%(rig.d['username'],time.time_ns())
    # The account home is discovered, rather than assumed from username.
    remote_home=rig.ssh('printf "%s" "$HOME"')
    backup=remote_home+'/globe-classroom-backup-'+str(time.time_ns())
    right=rig.d['screens']//2+1; left=right+1
    files=['/var/www/html/kmls.txt','/var/www/html/kml/slave_%s.kml'%right,'/var/www/html/kml/slave_%s.kml'%left]
    cmds=['set -eu','mkdir -p '+shlex.quote(backup)]
    for i,f in enumerate(files):
        cmds.append('if [ -f {f} ]; then cp -p {f} {b}/{i}; else touch {b}/{i}.absent; fi'.format(f=shlex.quote(f),b=shlex.quote(backup),i=i))
    rig.ssh('\n'.join(cmds))
    s.update(backup=backup,backup_files=files)
    save_state(s)

def deploy(s, scene_data=None, panel_path=None, camera_xml=None, branding_path=None):
    d=connection(); rig=Rig(d)
    host=rig.ssh('hostname')
    if not host: raise RuntimeError('SSH verification returned an empty hostname.')
    prepare_backup(rig,s)
    rig.ssh('mkdir -p '+shlex.quote(REMOTE))
    stage=s['stage']; token=str(time.time_ns())
    with tempfile.TemporaryDirectory(prefix='globe-classroom-') as temp:
        p=Path(temp)
        (p/'live.kml').write_bytes(networklink())
        (p/'scene-next.kml').write_bytes(scene_data if scene_data is not None else scene(stage))
        shutil.copyfile(panel_path if panel_path is not None else ROOT/'assets'/('%s.png'%stage),p/('panel-%s.png'%token))
        shutil.copyfile(branding_path if branding_path is not None else ROOT/'assets/branding.png',p/('branding-%s.png'%token))
        right=d['screens']//2+1; left=right+1
        (p/('slave_%s.kml'%right)).write_bytes(overlay(URL+'/panel-%s.png'%token))
        (p/('slave_%s.kml'%left)).write_bytes(overlay(URL+'/branding-%s.png'%token))
        rig.copy(list(p.iterdir()))
    # Preserve other applications' links. Bootstrap once; scenes refresh through live.kml.
    link=URL+'/live.kml'
    cmd='set -eu\n'
    cmd+='mv '+REMOTE+'/scene-next.kml '+REMOTE+'/scene.kml\n'
    cmd+='touch /var/www/html/kmls.txt\n'
    cmd+='grep -Fqx {u} /var/www/html/kmls.txt || printf "\\n%s\\n" {u} >> /var/www/html/kmls.txt\n'.format(u=shlex.quote(link))
    for n in [right,left]:
        cmd+='cp {r}/slave_{n}.kml /var/www/html/kml/slave_{n}.kml\n'.format(r=REMOTE,n=n)
    cmd+='printf "%s\\n" '+shlex.quote('flytoview='+(camera_xml if camera_xml is not None else camera(stage)))+' > /tmp/query.txt\n'
    rig.ssh(cmd)
    s['deployed_at']=time.time(); save_state(s)
    print('Deployed stage %s to %s; right panel lg%s, left branding lg%s.'%(stage,host,right,left))
    print('Check the rig visually. File transfer success does not prove Earth rendered the scene.')

def transition(s,action,verdict=None,evidence=''):
    s=json.loads(json.dumps(s)); stage=s['stage']
    if action=='hint':
        if stage in ('question','hint','partial'): s['stage']='hint'
        elif stage in ('transfer','transfer_hint','transfer_partial'): s['stage']='transfer_hint'
        else: raise RuntimeError('A hint is available only while a question is open.')
    elif action=='assess':
        group='transfer' if stage.startswith('transfer') else 'india'
        valid=('transfer','transfer_hint','transfer_partial') if group=='transfer' else ('question','hint','partial')
        if stage not in valid: raise RuntimeError('There is no open question to assess.')
        s['attempts'][group]+=1
        s['assessments'].append({'question':group,'verdict':verdict,'evidence':evidence[:600]})
        prefix='transfer_' if group=='transfer' else ''
        if verdict=='correct': s['stage']=prefix+'explain'
        elif verdict=='partial': s['stage']=prefix+'partial'
        else: s['stage']=prefix+'hint'
    elif action=='reveal':
        if stage in ('question','hint','partial'): s['stage']='explain'
        elif stage in ('transfer','transfer_hint','transfer_partial'): s['stage']='transfer_explain'
        else: raise RuntimeError('No open question to reveal.')
        s['assessments'].append({'question':'transfer' if stage.startswith('transfer') else 'india','verdict':'revealed','evidence':'Learner requested explanation; not evidence of mastery.'})
    elif action=='next':
        if stage=='explain': s['stage']='transfer'
        elif stage=='transfer_explain': s['stage']='recap'
        else: raise RuntimeError('Answer the open question first, or explicitly request reveal.')
    return s

def restore(s):
    if not s.get('backup'): raise RuntimeError('There is no display backup for this lesson.')
    rig=Rig(connection())
    # Serve an empty scene FIRST: removing a loading-list URL alone can leave
    # geometry in a cached, still-loaded NetworkLink in Google Earth.
    rig.ssh('mkdir -p '+shlex.quote(REMOTE))
    with tempfile.TemporaryDirectory(prefix='classroom-cleanup-') as folder:
        p=Path(folder)/'scene-empty.kml'; p.write_bytes(xml(document()[0])); rig.copy([p])
    rig.ssh('mv '+shlex.quote(REMOTE+'/scene-empty.kml')+' '+shlex.quote(REMOTE+'/scene.kml')+'; sleep 3')
    # Preserve links added by other applications after the lesson began.
    # Restore a shared side file only while it still belongs to this skill.
    script="""from pathlib import Path
import json
backup=Path(BACKUP)
files=FILES
prefix=PREFIX
empty=EMPTY
loading=Path('/var/www/html/kmls.txt')
if loading.exists():
    lines=[v for v in loading.read_text().splitlines() if v.strip() and not v.strip().startswith(prefix)]
    loading.write_text('\\n'.join(lines)+('\\n' if lines else ''))
for i,name in enumerate(files):
    if i==0: continue
    target=Path(name)
    if not target.exists() or prefix not in target.read_text(errors='replace'): continue
    if (backup/(str(i)+'.absent')).exists(): target.write_bytes(empty)
    else: target.write_bytes((backup/str(i)).read_bytes())
"""
    script=script.replace('BACKUP',repr(s['backup'])).replace('FILES',repr(s['backup_files'])).replace('PREFIX',repr(URL+'/')).replace('EMPTY',repr(xml(document()[0])))
    rig.ssh('python3 -',data=script.encode('utf-8'))
    s['restored']=True; s['ended_at']=time.time(); save_state(s)
    print('Ended classroom: served an empty scene before removing classroom loading links.')
    print('Restored classroom-owned side overlays; retained other applications’ current content, lesson records and backups.')
    print('Camera position unchanged. Confirm markers and classroom panels disappeared on the rig; HTTP/file success is not visual proof.')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['start','status','hint','assess','reveal','next','continue','restore','render'])
    ap.add_argument('--verdict',choices=['correct','partial','incorrect','unclear'])
    ap.add_argument('--evidence',default='',help='Brief assessment reasoning; never include credentials')
    ap.add_argument('--stage',choices=STAGES,default='question')
    ap.add_argument('--output',type=Path,default=Path('/tmp/globe-classroom-preview'))
    a=ap.parse_args()
    if a.action=='render':
        a.output.mkdir(parents=True,exist_ok=True)
        (a.output/'scene.kml').write_bytes(scene(a.stage))
        (a.output/'live.kml').write_bytes(networklink())
        (a.output/'panel.kml').write_bytes(overlay(URL+'/preview.png'))
        (a.output/'camera.txt').write_text('flytoview='+camera(a.stage)+'\n')
        print('Generated XML locally at '+str(a.output)); return
    if a.action=='start':
        old=read_state() if STATE.exists() else {}
        s={'version':1,'stage':'question','attempts':{'india':0,'transfer':0},'assessments':[]}
        if old.get('backup') and not old.get('restored'):
            for k in ['backup','backup_files']: s[k]=old[k]
    else: s=read_state()
    if a.action=='status':
        print(json.dumps({k:v for k,v in s.items() if k not in ['backup_files']},indent=2)); return
    if a.action=='restore': restore(s); return
    if s.get('restored') and a.action!='start': raise RuntimeError('Lesson restored. Run start for a new session.')
    if a.action=='assess' and not a.verdict: ap.error('assess requires --verdict')
    if a.action in ['hint','assess','reveal','next']: s=transition(s,a.action,a.verdict,a.evidence)
    deploy(s)

if __name__=='__main__':
    try: main()
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as e:
        print('Classroom error: '+str(e),file=sys.stderr); sys.exit(1)
