# -*- coding: utf-8 -*-
import os, random
from psychopy import core, visual, event, data, gui, logging


practice_trials = 16
main_trials = 50
n_blocks = 5
rt_limit = 1.5 
cue_duration = 2.0  
iti_duration = 0.2 

expInfo = {'Participant ID': '', 'Session': '001'}
dlg = gui.DlgFromDict(expInfo, title='')
if not dlg.OK:
    core.quit()

dataDir = 'data'
if not os.path.exists(dataDir):
    os.makedirs(dataDir)
    
expName = 'FlankerSwitchTask'
dateStr = data.getDateStr()
filename = os.path.join(dataDir, f"{expInfo['Participant ID']}_{expName}_{dateStr}")
thisExp = data.ExperimentHandler(name=expName,
                              extraInfo=expInfo,
                              dataFileName=filename)


win = visual.Window(fullscr=True, color='white', units='norm')
logging.console.setLevel(logging.WARNING)

def check_exit(keys):
    if 'escape' in keys:
        thisExp.saveAsWideText(filename + '.csv')
        win.close(); core.quit()


instr = {
    'welcome':       "In this task, you will respond to different visual stimuli as quickly and accurately as possible\n\nPress Space Bar to continue",
    'features':      "You will need to pay attention to either the arrows that can point up, down, left and right or shapes that can be coloured (black) or blank (white).\n\nPress Space Bar to continue",
    'bg_map':        "In this task, the background will be red, blue, or white.\n\nA red background indicates that you should focus on the outside shapes or arrows.\nA blue background indicates that you should focus on the shape in the middle.\nA white background will contain a word, either inside or outside, that tells you where to look.\n\nPress Space Bar to continue",
    'before_blocks': "Before each Block (5 in total) you will have time to practice\n\nPress Space Bar to continue",
    'start_block':   "BLOCK {blockNum}\n\nPress Space Bar to continue",
    'practice':      "Let's Practice\n\nPress Space Bar to continue",
    'begin_trials':  "Now the trials are about to start. Please respond as quickly and accurately as possible\n\nPress Space Bar when you are ready",
    'thanks':        "Thank you! This task is now finished\n\nPress Space Bar to exit"
}

def show_text(key, **fmt):
    win.color = 'white'
    win.flip()
    txt = instr[key].format(**fmt)
    stim = visual.TextStim(win, text=txt,
        height=0.08, wrapWidth=1.4, color='black')
    stim.draw(); win.flip()
    while True:
        keys = event.waitKeys(keyList=['space','escape'])
        check_exit(keys)
        if 'space' in keys: break


positions = [(-0.4,0.4),(0,0.4),(0.4,0.4),(-0.4,0),(0,0),(0.4,0),(-0.4,-0.4),(0,-0.4),(0.4,-0.4)]

def make_arrow(direction, pos):
    sym = '←' if direction=='left' else '→'
    return visual.TextStim(win, text=sym,
        pos=pos, height=0.15, color='black', font='Arial Unicode MS')

def make_shape(is_triangle, pos):
    if is_triangle:
        return visual.ShapeStim(win,
            vertices=[(-.1,-.1),(0,.12),(.1,-.1)],
            pos=pos, fillColor='black', lineColor='black')
    else:
        return visual.Circle(win,
            radius=0.1, pos=pos,
            fillColor='black', lineColor='black')


def run_trials(nTrials):
    n_correct = 0
    half = nTrials // 2
    trial_list = ['shape']*half + ['arrow']*half
    random.shuffle(trial_list)

    for t, attend in enumerate(trial_list, start=1):
        if attend == 'shape':
            color = random.choice(['red','blue'])
            win.color = color
            win.flip()
            core.wait(cue_duration)
        else:
            win.color = 'white'
            win.flip()
            focus_word = random.choice(['inside','outside'])
            core.wait(cue_duration)

        stimuli = []
        if attend == 'shape':
            center_tri = random.choice([True, False])
            flank = [not center_tri]*8
            correctKey = 'a' if center_tri else 'l'
            config = flank[:4] + [center_tri] + flank[4:]
            for pos, tri in zip(positions, config):
                stimuli.append(make_shape(tri, pos))
        else:
            center_dir = random.choice(['left','right'])
            flank_dir = 'right' if center_dir == 'left' else 'left'
            correctKey = 'a' if center_dir=='left' else 'l'
            for i, pos in enumerate(positions):
                if i == 4: 
                    stimuli.append(make_arrow(center_dir, pos))
                else: 
                    stimuli.append(make_arrow(flank_dir, pos))

        win.color = color if attend == 'shape' else 'white'
        for stim in stimuli:
            stim.draw()
        
        if attend == 'arrow':
            visual.TextStim(win, text=focus_word,
                pos=(0,-0.6), height=0.1, color='black').draw()
        
        win.flip()
        trial_onset = core.getTime()

        keys = event.waitKeys(
            maxWait=rt_limit,
            keyList=['a','l','escape'],
            timeStamped=core.Clock()
        )
        
        if keys:
            response, rt = keys[0]
            check_exit([response])
            rt = rt - trial_onset  
        else:
            response = ''
            rt = rt_limit

        win.color = 'white'
        win.flip()
        core.wait(iti_duration)

        correct = int(response == correctKey)
        n_correct += correct
        thisExp.addData('trial', t)
        thisExp.addData('attend', attend)
        if attend == 'shape':
            thisExp.addData('center_is_triangle', center_tri)
            thisExp.addData('bg_color', color)
        else:
            thisExp.addData('center_arrow', center_dir)
            thisExp.addData('focus_word', focus_word)
        thisExp.addData('respKey', response)
        thisExp.addData('accuracy', correct)
        thisExp.addData('rt', rt)
        thisExp.nextEntry()

    return n_correct / nTrials

show_text('welcome')
show_text('features')
show_text('bg_map')
show_text('before_blocks')

for block in range(1, n_blocks+1):
    show_text('start_block', blockNum=block)
    show_text('practice')
    while True:
        acc = run_trials(practice_trials)
        win.color = 'white'
        win.flip()
        fb_txt = (f"Practice Accuracy: {acc*100:.0f}%\n\nPress Space Bar to continue"  
                  if acc>=practice_threshold
                  else f"Practice Accuracy: {acc*100:.0f}%\n\nPress Space Bar to retry practice")
        fb = visual.TextStim(win, text=fb_txt,
            height=0.07, wrapWidth=1.4, color='black')
        fb.draw(); win.flip()
        keys = event.waitKeys(keyList=['space','escape'])
        check_exit(keys)
        if acc>=practice_threshold: break

    show_text('begin_trials')
    run_trials(main_trials)

show_text('thanks')
thisExp.saveAsWideText(filename + '.csv')
win.close()
core.quit()