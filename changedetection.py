from psychopy import visual, core, event, data, gui
import random

info_dlg = gui.Dlg(title="Change Detection Task")
info_dlg.addText("Participant Info")
info_dlg.addField("Participant ID:")
info_dlg.addField("Session:", initial="001")
info_dlg.show()

if info_dlg.OK:
    exp_info = {'participant': info_dlg.data[0], 'session': info_dlg.data[1]}
else:
    core.quit()

filename = f"data/{exp_info['participant']}_session{exp_info['session']}"
this_exp = data.ExperimentHandler(name='ChangeDetection', version='',
                                extraInfo=exp_info, runtimeInfo=None,
                                originPath=None, savePickle=True, saveWideText=True,
                                dataFileName=filename)

win = visual.Window(size=[1280, 720], color='gray', units='height', fullscr=False)
press_text = visual.TextStim(win, text="Press space bar to continue", pos=(0, -0.3), height=0.03)

def show_text(message, height=0.035, wait_keys=['space'], show_press_text=True, center_text=False):
    if center_text:
        pos = (0, 0)
    else:
        pos = (0, 0.3)
    text = visual.TextStim(win, text=message, color='white', height=height, wrapWidth=1.2, pos=pos)
    text.draw()
    if show_press_text:
        press_text.draw()
    win.flip()
    if wait_keys:
        event.waitKeys(keyList=wait_keys)

def show_fixation(duration=0.8):
    fixation = visual.TextStim(win, text="+", pos=(0, 0), color='white', height=0.05)
    fixation.draw()
    win.flip()
    core.wait(duration)

def create_arrow(direction):
    if direction == 'left':
        arrow = visual.ShapeStim(win,
            vertices=[[0.04, 0], [-0.02, 0], [-0.02, 0.03], [-0.06, 0], [-0.02, -0.03], [-0.02, 0]],
            fillColor='white', lineColor='white', closeShape=True, pos=(0, 0.15))
    else: 
        arrow = visual.ShapeStim(win, 
            vertices=[[-0.04, 0], [0.02, 0], [0.02, 0.03], [0.06, 0], [0.02, -0.03], [0.02, 0]],
            fillColor='white', lineColor='white', closeShape=True, pos=(0, 0.15))
    return arrow

fixation = visual.TextStim(win, text="+", pos=(0, 0), color='white', height=0.075)

def show_arrow(direction):
    arrow = create_arrow(direction)
    arrow.draw()
    fixation.draw()
    win.flip()
    core.wait(0.2)  
    win.flip()
    core.wait(0.3)  

square_size = 0.05
spacing_x = 0.25
spacing_y = 0.1

left_positions = [(-spacing_x * 2.1, -0.15), (-spacing_x * 1.1, 0.0), (-spacing_x * 1.5, spacing_y),
                  (-spacing_x * 1.8, -0.25), (-spacing_x * 0.8, 0.2), (-spacing_x * 2.0, 0.1)]
right_positions = [(spacing_x * 0.8, 0.05), (spacing_x * 1.8, 0.025), (spacing_x * 1.1, -spacing_y),
                   (spacing_x * 0.5, -0.2), (spacing_x * 2.0, 0.15), (spacing_x * 1.3, 0.25)]

colors = ['pink', 'orange', 'blue', 'yellow', 'green', 'red', 'purple', 'cyan', 'white',
          'brown', 'lime', 'teal', 'navy', 'maroon', 'olive', 'silver', 'gold']

def draw_squares(positions, colors_to_show):
    for pos, color in zip(positions, colors_to_show):
        visual.Rect(win, width=square_size, height=square_size, fillColor=color, lineColor='black', pos=pos).draw()

def run_trial(direction, num_squares, with_feedback=True):
    if direction == 'left':
        positions = left_positions[:num_squares]
        other_positions = right_positions[:num_squares]
    else:
        positions = right_positions[:num_squares]
        other_positions = left_positions[:num_squares]

    main_colors = random.sample(colors, num_squares)
    
    remaining_colors = [c for c in colors if c not in main_colors]
    if len(remaining_colors) < num_squares:
        other_colors = random.choices(remaining_colors, k=num_squares)
    else:
        other_colors = random.sample(remaining_colors, num_squares)
    
    trial_type = random.choice(['same', 'one_change', 'all_different'])

    if trial_type == 'same':
        second_main_colors = main_colors.copy()
    elif trial_type == 'one_change':
        second_main_colors = main_colors.copy()
        changed_idx = random.randint(0, num_squares-1)
        available_colors = [c for c in colors if c != main_colors[changed_idx]]
        second_main_colors[changed_idx] = random.choice(available_colors)
    else: 
        available_colors = [c for c in colors if c not in main_colors]
        if len(available_colors) < num_squares:
            second_main_colors = random.choices(available_colors, k=num_squares)
        else:
            second_main_colors = random.sample(available_colors, num_squares)
    
    show_arrow(direction)

    if direction == 'left':
        draw_squares(left_positions[:num_squares], main_colors)
        draw_squares(right_positions[:num_squares], other_colors)
    else:
        draw_squares(right_positions[:num_squares], main_colors)
        draw_squares(left_positions[:num_squares], other_colors)
    win.flip()
    core.wait(0.1)

    win.flip()
    core.wait(0.9)

    if direction == 'left':
        draw_squares(left_positions[:num_squares], second_main_colors)
        draw_squares(right_positions[:num_squares], other_colors)
    else:
        draw_squares(right_positions[:num_squares], second_main_colors)
        draw_squares(left_positions[:num_squares], other_colors)
    win.flip()
    core.wait(0.75)

    question = visual.TextStim(win, text="Were the colors the same or different?\n\nA - Same\nL - Different", 
                             color='white', height=0.035, pos=(0, 0))
    question.draw()
    win.flip()
    timer = core.Clock()
    keys = event.waitKeys(keyList=['a', 'l'], timeStamped=timer)
    response, rt = keys[0]

    correct = (response == 'a' and trial_type == 'same') or (response == 'l' and trial_type != 'same')
    
    if with_feedback:
        feedback = visual.TextStim(win, text="Correct" if correct else "Incorrect",
                                 height=0.04, color='green' if correct else 'red', pos=(0, 0))
        feedback.draw()
        win.flip()
        core.wait(1.0)
    else:
        win.flip()
        core.wait(1.0)

    this_exp.addData('direction', direction)
    this_exp.addData('num_squares', num_squares)
    this_exp.addData('response', response)
    this_exp.addData('rt', rt)
    this_exp.addData('correct', correct)
    this_exp.addData('trial_type', trial_type)
    this_exp.nextEntry()
    
    return correct

show_text("In this next task, you will be required to memorize and detect changes in a set of visual stimuli")
show_text("At first you will see an arrow above a centered cross pointing either to the left or to the right. This will tell you which side of the screen you need to memorize")

text = visual.TextStim(win, text="In this example, you would need to memorize the squares on the left side of the screen", color='white', height=0.035, pos=(0, 0.3))
text.draw()
arrow = create_arrow('left')
arrow.draw()
fixation.draw()
win.flip()
event.waitKeys(keyList=['space'])

text = visual.TextStim(win, text="Therefore you need to memorize the blue, orange, and pink square", color='white', height=0.035, pos=(0, 0.3))
fixation.draw()
left_colors = ['pink', 'orange', 'blue']
right_colors = ['yellow', 'green', 'red']
text.draw()
draw_squares(left_positions[:3], left_colors)
draw_squares(right_positions[:3], right_colors)
press_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

show_text("After a small delay you will be presented with the squares again in either of two formats:\n\na) All of the squares remained the same color\nb) One of the squares changed color")
show_text("Your task is to decide if the colors are the same (by pressing the letter “A” in the keyboard), or if they changed (by pressing the \nletter “L” on the keyboard)")
show_text("Let's do some practice trials", show_press_text=True)

practice_passed = False
while not practice_passed:
    correct_count = 0
    total_trials = 0
    
    for num_squares in range(2, 7):
        for _ in range(2):
            correct = run_trial(direction=random.choice(['left', 'right']), num_squares=num_squares, with_feedback=True)
            if correct:
                correct_count += 1
            total_trials += 1
    
    accuracy = correct_count / total_trials
    if accuracy >= 0.75:
        practice_passed = True
    else:
        continue

show_text("From now on, feedback will not be provided.\nThe task will consist of 5 blocks\n\nPress space bar when you are ready to start")

for block_num in range(1, 6):
    block_title = visual.TextStim(win, text=f"BLOCK {block_num}", height=0.05, color='white')
    block_title.draw()
    win.flip()
    core.wait(2.0)

    for num_squares in range(2, 7):
        directions = ['left'] * 5 + ['right'] * 5
        random.shuffle(directions)
        
        for direction in directions:
            run_trial(direction, num_squares, with_feedback=False)

    if block_num < 5:
        show_text(f"You reached the end of Block {block_num}.\nBlock {block_num + 1} will start in 30 seconds", 
                 show_press_text=False, wait_keys=None)
        core.wait(30.0)

show_text("Thank you\nThis task is now finished\n\nPress space bar to continue")
win.close()
core.quit()