#!/usr/bin/env python3
"""Install the skill into an existing Nara profile; does not contact the rig."""
import argparse
from pathlib import Path
import shutil
import time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--profile',default='liquid-galaxy-agent')
args=parser.parse_args()
if not args.profile or '/' in args.profile or args.profile in ('.','..'):
    parser.error('Supply a profile name, not a path.')
home=Path.home()/'.hermes/profiles'/args.profile
if not home.is_dir():
    parser.error('Profile not found: '+str(home))
source=Path(__file__).resolve().parent
dest=home/'skills/liquid-galaxy/globe-classroom'
if source==dest:
    parser.error('Already inside the installation directory.')
if dest.exists():
    backup=home/'backups'/('globe-classroom-'+str(time.time_ns()))
    backup.parent.mkdir(parents=True,exist_ok=True)
    shutil.move(str(dest),str(backup))
    print('Previous skill backed up at:',backup)
dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copytree(source,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
print('Installed:',dest)
print('No rig content changed. Existing lesson state and connection are preserved.')
print('In Nara: reload globe-classroom and resume the active lesson using lesson_engine.py.')
