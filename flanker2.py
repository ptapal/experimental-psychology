# -*- coding: utf-8 -*-
import os, random
from psychopy import core, visual, event, data, gui, logging
import numpy as np

practice_trials = 16  
main_trials = 50
n_blocks = 4
rt_limit = 1.5
iti_duration = 0.2
required_accuracy = 0.75  

expInfo = {'Participant ID': '', 'Session': '001'}
dlg = gui.DlgFromDict(expInfo, title='Flanker Task')
if not dlg.OK:
    core.quit()

dataDir = 'data'
if not os.path.exists(dataDir):
    os.makedirs(dataDir)

filename = os.path.join(dataDir, f"{expInfo['Participant ID']}_FlankerTask_{data.getDateStr()}")
thisExp = data.ExperimentHandler(name='FlankerTask',
                              extraInfo=expInfo,
                              dataFileName=filename)

win = visual.Window(fullscr=True, color='white', units='norm')

def check_exit(keys):
    if 'escape' in keys:
        thisExp.saveAsWideText(filename + '.csv')
        win.close()
        core.quit()

def make_shape_with_stripes(is_triangle, line_direction, pos, size=0.1):
    if is_triangle:
        vertices = np.array([[-size, -size], [0, size*1.5], [size, -size]])
        shape = visual.ShapeStim(win,
            vertices=vertices,
            pos=pos, fillColor='white', lineColor='black')
    else:
        shape = visual.Circle(win,
            radius=size, pos=pos,
            fillColor='white', lineColor='black')


    stripes = []
    spacing = 0.025 

    angle = np.pi / 4 if line_direction == 'left' else -np.pi / 4
    direction = np.array([np.cos(angle), np.sin(angle)])
    perp = np.array([-direction[1], direction[0]]) 

    for i in range(8):
        offset = (i - 4 + 0.5) * spacing
        origin = np.array(pos) + offset * perp

        line_start = origin - 2 * direction
        line_end = origin + 2 * direction

        if is_triangle:
            abs_vertices = vertices + np.array(pos)

            intersections = []
            for j in range(3):
                p1 = abs_vertices[j]
                p2 = abs_vertices[(j + 1) % 3]
                inter = segment_intersection(line_start, line_end, p1, p2)
                if inter is not None:
                    intersections.append(inter)

            if len(intersections) == 2:
                xys = np.array(intersections)
                line = visual.Line(win, start=xys[0], end=xys[1],
                                   lineColor='black', lineWidth=3)
                stripes.append(line)
        else:
            intersections = circle_line_intersections(np.array(pos), size, line_start, line_end)
            if len(intersections) == 2:
                xys = np.array(intersections)
                line = visual.Line(win, start=xys[0], end=xys[1],
                                   lineColor='black', lineWidth=3)
                stripes.append(line)

    return shape, stripes

def segment_intersection(p1, p2, q1, q2):
    """Find intersection point between segments p1–p2 and q1–q2"""
    A = np.array([[p2[0] - p1[0], q1[0] - q2[0]],
                  [p2[1] - p1[1], q1[1] - q2[1]]])
    b = np.array([q1[0] - p1[0], q1[1] - p1[1]])
    try:
        t, u = np.linalg.solve(A, b)
        if 0 <= t <= 1 and 0 <= u <= 1:
            return p1 + t * (p2 - p1)
    except np.linalg.LinAlgError:
        pass
    return None

def circle_line_intersections(center, radius, p1, p2):
    """Return two points where line intersects the circle"""
    d = p2 - p1
    f = p1 - center
    a = np.dot(d, d)
    b = 2 * np.dot(f, d)
    c = np.dot(f, f) - radius ** 2

    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return []

    sqrt_disc = np.sqrt(discriminant)
    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)

    intersections = []
    for t in [t1, t2]:
        if 0 <= t <= 1 or True: 
            intersections.append(p1 + t * d)
    return intersections

def run_trial(trial_type, is_practice=False):
    win.color = 'white'
    

    if trial_type == 'shape':
        center_shape = random.choice(['triangle', 'circle'])
        center_line = random.choice(['left', 'right'])
        flank_shape = 'circle' if center_shape == 'triangle' else 'triangle'
        flank_line = center_line 
        correct_key = 'a' if center_shape == 'triangle' else 'l'
    else:
        center_line = random.choice(['left', 'right'])
        center_shape = random.choice(['triangle', 'circle'])
        flank_line = 'right' if center_line == 'left' else 'left' 
        flank_shape = random.choice(['triangle', 'circle'])
        correct_key = 'a' if center_line == 'left' else 'l'
    
    fixation = visual.TextStim(win, text='+', height=0.2, color='black')
    
    positions = [(-0.5,0), (-0.25,0), (0,0), (0.25,0), (0.5,0)]
    stimuli = []
    for i, pos in enumerate(positions):
        if i == 2: 
            shape, stripes = make_shape_with_stripes(center_shape == 'triangle', center_line, pos)
        else: 
            shape, stripes = make_shape_with_stripes(flank_shape == 'triangle', flank_line, pos)
        stimuli.append((shape, stripes))
    

    instruction = visual.TextStim(win,
        text="Focus on SHAPE" if trial_type == 'shape' else "Focus on LINE ORIENTATION",
        pos=(0, -0.6), height=0.08, color='black')
    
    reminder = visual.TextStim(win,
        text="A (triangle/left)    L (circle/right)",
        pos=(0, -0.8), height=0.06, color='black')
    
    fixation.draw()
    for shape, stripes in stimuli:
        shape.draw()
        for stripe in stripes:
            stripe.draw()
    instruction.draw()
    reminder.draw()
    
    win.flip()
    trial_onset = core.getTime()
    
    keys = event.waitKeys(maxWait=rt_limit,
                        keyList=['a','l','escape'],
                        timeStamped=core.Clock())
    
    if keys:
        response, rt = keys[0]
        if response == 'escape':
            check_exit([response])
        rt = rt - trial_onset
    else:
        response = ''
        rt = rt_limit
    
    win.color = 'white'
    fixation.draw()
    win.flip()
    core.wait(iti_duration)
    
    thisExp.addData('trial_type', trial_type)
    thisExp.addData('is_practice', int(is_practice))
    thisExp.addData('center_shape', center_shape)
    thisExp.addData('center_line', center_line)
    thisExp.addData('flank_shape', flank_shape)
    thisExp.addData('flank_line', flank_line)
    thisExp.addData('response', response)
    thisExp.addData('rt', rt)
    thisExp.addData('correct', int(response == correct_key))
    thisExp.nextEntry()
    
    return int(response == correct_key)

def show_instructions():
    texts = [
        "Flanker Task\n\nPress space bar to continue",
        "In this task, you will respond to different visual stimuli\nas quickly and accurately as possible\n\nPress space bar to continue",
        "You will need to pay attention to either:\n- The SHAPE (circle or triangle)\n- Or the LINE ORIENTATIONS (left or right)\n\nPress space bar to continue",
        "The instruction will tell you which feature to focus on\nat the beginning of each trial\n\nPress space bar to continue"
    ]
    
    for text in texts:
        win.color = 'white'
        visual.TextStim(win, text=text, height=0.06, color='black', wrapWidth=1.8).draw()
        win.flip()
        keys = event.waitKeys(keyList=['space','escape'])
        if 'escape' in keys:
            check_exit(['escape'])
    
    win.color = 'white'
    
    shape1, stripes1 = make_shape_with_stripes(True, 'left', (-0.3, 0.3), size=0.15)
    text1 = visual.TextStim(win, text="SHAPE example:", pos=(-0.3, 0.6), height=0.06, color='black')
    answer1 = visual.TextStim(win, text="Press 'A' for triangle", pos=(-0.3, -0.4), height=0.06, color='black')
    
    shape2, stripes2 = make_shape_with_stripes(False, 'right', (0.3, 0.3), size=0.15)
    text2 = visual.TextStim(win, text="SHAPE example:", pos=(0.3, 0.6), height=0.06, color='black')
    answer2 = visual.TextStim(win, text="Press 'L' for circle", pos=(0.3, -0.4), height=0.06, color='black')
    
    instruction = visual.TextStim(win, 
        text="When focusing on SHAPE:\nPress 'A' for triangle, 'L' for circle\n\nPress space bar to continue", 
        pos=(0, -0.7), height=0.06, color='black')
        
    text1.draw()
    shape1.draw()
    for stripe in stripes1:
        stripe.draw()
    answer1.draw()
    
    text2.draw()
    shape2.draw()
    for stripe in stripes2:
        stripe.draw()
    answer2.draw()
    
    instruction.draw()
    win.flip()
    event.waitKeys(keyList=['space','escape'])
    
    win.color = 'white'
    
    shape3, stripes3 = make_shape_with_stripes(True, 'left', (-0.3, 0.3), size=0.15)
    text3 = visual.TextStim(win, text="LINE example:", pos=(-0.3, 0.6), height=0.06, color='black')
    answer3 = visual.TextStim(win, text="Press 'A' for left", pos=(-0.3, -0.4), height=0.06, color='black')
    
    shape4, stripes4 = make_shape_with_stripes(False, 'right', (0.3, 0.3), size=0.15)
    text4 = visual.TextStim(win, text="LINE example:", pos=(0.3, 0.6), height=0.06, color='black')
    answer4 = visual.TextStim(win, text="Press 'L' for right", pos=(0.3, -0.4), height=0.06, color='black')
    
    instruction = visual.TextStim(win, 
        text="When focusing on LINE ORIENTATION:\nPress 'A' for left, 'L' for right\n\nPress space bar to continue", 
        pos=(0, -0.7), height=0.06, color='black')
    
    text3.draw()
    shape3.draw()
    for stripe in stripes3:
        stripe.draw()
    answer3.draw()
    
    text4.draw()
    shape4.draw()
    for stripe in stripes4:
        stripe.draw()
    answer4.draw()
    
    instruction.draw()
    win.flip()
    event.waitKeys(keyList=['space','escape'])
    
    win.color = 'white'
    visual.TextStim(win, 
        text="Now let's practice with some trials\n\nRemember:\n- Focus on the center figure\n- Respond as quickly and accurately as possible\n\nPress space bar to begin practice", 
        height=0.06, color='black', wrapWidth=1.8).draw()
    win.flip()
    event.waitKeys(keyList=['space','escape'])

def run_practice():
    correct_count = 0
    trial_count = 0
    
    while True:
        trial_type = random.choice(['shape', 'line'])
        correct = run_trial(trial_type, is_practice=True)
        correct_count += correct
        trial_count += 1
        
        if trial_count >= practice_trials:
            current_accuracy = correct_count / trial_count
            if current_accuracy >= required_accuracy:
                break
    
    win.color = 'white'
    final_accuracy = correct_count / trial_count
    feedback_text = f"Practice completed!\n\nAccuracy: {int(final_accuracy*100)}%\n\nPress space bar to begin the main task"
    visual.TextStim(win, text=feedback_text, height=0.06, color='black').draw()
    win.flip()
    event.waitKeys(keyList=['space','escape'])

show_instructions()

run_practice()

win.color = 'white'
visual.TextStim(win, 
    text="From now on the trials will have a time limit.\nRemember to respond as fast and accurately as possible.\n\nPress space bar to continue", 
    height=0.06, color='black').draw()
win.flip()
event.waitKeys(keyList=['space','escape'])

for block in range(n_blocks):
    win.color = 'white'
    visual.TextStim(win, text=f"BLOCK {block+1}\n\nPress space bar to begin", 
                   height=0.08, color='black').draw()
    win.flip()
    event.waitKeys(keyList=['space','escape'])
    
    for trial in range(main_trials):
        trial_type = random.choice(['shape', 'line'])
        run_trial(trial_type, is_practice=False)
    
    if block < n_blocks - 1:
        win.color = 'white'
        visual.TextStim(win, 
                       text=f"End of Block {block+1}\nTake a break if needed\n\nPress space bar to continue", 
                       height=0.06, color='black').draw()
        win.flip()
        event.waitKeys(keyList=['space','escape'])

win.color = 'white'
visual.TextStim(win, 
               text="Thank you\nThis task is now finished\n\nPress space bar to exit", 
               height=0.08, color='black').draw()
win.flip()
event.waitKeys(keyList=['space','escape'])

thisExp.saveAsWideText(filename + '.csv')
win.close()
core.quit()