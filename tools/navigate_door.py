"""Bounded first-room navigation through controller input only."""
import json
import math
from pathlib import Path
import time
from room_state import command,state

out=Path(__file__).resolve().parents[1]/'local/newgame-probe'
history=[]
def press(mask,seconds):
    try:
        command('set_input',buttons=f'{mask:04X}')
        time.sleep(seconds)
    finally:
        command('clear_input')
    time.sleep(.08)

initial=state()
if len(initial['doors']) != 1:
    raise SystemExit('This bounded probe expects one exit')
target=initial['doors'][0]['tile']
target=[target[0]*128+64,target[1]*128+64]
calibration=[]
for mask in (0xFFEF,0xFFDF):
    before=state()['position']
    press(mask,.08)
    after=state()['position']
    calibration.append([after[0]-before[0],after[2]-before[2]])
directions=[(0xFFEF,calibration[0]),(0xFFBF,[-v for v in calibration[0]]),
            (0xFFDF,calibration[1]),(0xFF7F,[-v for v in calibration[1]])]
for index in range(32):
    current=state()
    history.append(current)
    if current['room'] != initial['room']:
        break
    delta=[target[0]-current['position'][0],target[1]-current['position'][2]]
    if math.hypot(*delta)<100:
        press(0xBFFF,.12)
        time.sleep(.3)
        if state()['room'] != initial['room']:
            break
    scored=sorted(directions,key=lambda x:sum(a*b for a,b in zip(x[1],delta))/(math.hypot(*x[1]) or 1),reverse=True)
    mask,vector=scored[0]
    if math.hypot(*vector)<1:
        raise SystemExit('Insufficient movement calibration')
    seconds=min(.18,max(.03,math.hypot(*delta)/(math.hypot(*vector)/.08)*.6))
    press(mask,seconds)
    after=state()
    if after['position']==current['position']:
        press(scored[1][0],.1)
result=dict(initial=initial,calibration=calibration,final=state(),history=history)
result['changed_room']=result['final']['room']!=initial['room']
(out/'navigation.json').write_text(json.dumps(result,indent=2))
command('screenshot_file',path=str(out/'navigation.png'))
print(json.dumps({k:v for k,v in result.items() if k!='history'},indent=2))
