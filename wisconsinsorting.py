from psychopy import visual, core, event, gui, data
import random
import os

info_dlg = gui.Dlg(title="Wisconsin Card Sorting Task")
info_dlg.addText("Participant Info")
info_dlg.addField("Participant ID:")
info_dlg.addField("Session:", initial="1")
info_dlg.show()

if info_dlg.OK:
    exp_info = {'participant': info_dlg.data[0], 'session': info_dlg.data[1]}
else:
    core.quit()

if not os.path.exists('data'):
    os.makedirs('data')

filename = f"data/WCST_{exp_info['participant']}_session{exp_info['session']}"
this_exp = data.ExperimentHandler(name='WCST', version='1.0',
                                extraInfo=exp_info, runtimeInfo=None,
                                originPath=None, savePickle=True, saveWideText=True,
                                dataFileName=filename)

win = visual.Window([1024, 768], monitor="testMonitor", units="norm", fullscr=False, color='white')

rules = ['color', 'shape', 'number']
current_rule = random.choice(rules)
correct_in_row = 0
rule_changes = 0

script_dir = os.path.dirname(os.path.abspath(__file__))
wisconsin_path = os.path.join(script_dir, "Wisconsin_Material")
all_images = list(range(1, 65))

def get_card_properties(image_num):
    number = (image_num - 1) % 4 + 1
    group = (image_num - 1) // 16
    color_group = ((image_num - 1) % 16) // 4
    shapes = ['triangle', 'circle', 'star', 'cross']
    colors = ['green', 'red', 'blue', 'yellow']
    return {'number': number, 'shape': shapes[group], 'color': colors[color_group], 'image_num': image_num}

def get_image_path(num):
    return os.path.join(wisconsin_path, f"{num}.jpg")

missing_files = []
for num in all_images:
    if not os.path.exists(get_image_path(num)):
        missing_files.append(get_image_path(num))

if missing_files:
    error_msg = "Missing image files:\n" + "\n".join(missing_files)
    raise FileNotFoundError(error_msg)

instructions = [
    "Wisconsin Card Sorting",
    "In this next task, you will need to classify cards in base of their number of items, the shape of their items, or the color of their items\n\nPress space bar to continue"
]

def select_reference_cards(bottom_card):
    color_matches = []
    shape_matches = []
    number_matches = []
    
    for num in all_images:
        if num == bottom_card['image_num']:
            continue
        props = get_card_properties(num)
        if props['color'] == bottom_card['color']:
            color_matches.append(num)
        if props['shape'] == bottom_card['shape']:
            shape_matches.append(num)
        if props['number'] == bottom_card['number']:
            number_matches.append(num)
    
    selected = []
    if color_matches:
        selected.append(random.choice(color_matches))
    if shape_matches:
        selected.append(random.choice(shape_matches))
    if number_matches:
        selected.append(random.choice(number_matches))
    
    while len(selected) < 4:
        remaining = [num for num in all_images if num != bottom_card['image_num'] and num not in selected]
        if not remaining:
            break
        selected.append(random.choice(remaining))
    
    matches = 0
    for num in selected:
        props = get_card_properties(num)
        if (props['color'] == bottom_card['color'] or 
            props['shape'] == bottom_card['shape'] or 
            props['number'] == bottom_card['number']):
            matches += 1
    
    if matches < 2:
        for i in range(len(selected)):
            props = get_card_properties(selected[i])
            if not (props['color'] == bottom_card['color'] or 
                   props['shape'] == bottom_card['shape'] or 
                   props['number'] == bottom_card['number']):
                for rule in ['color', 'shape', 'number']:
                    if rule == 'color' and color_matches:
                        selected[i] = random.choice(color_matches)
                        break
                    elif rule == 'shape' and shape_matches:
                        selected[i] = random.choice(shape_matches)
                        break
                    elif rule == 'number' and number_matches:
                        selected[i] = random.choice(number_matches)
                        break
    
    return selected[:4]

def show_example_trial():
    example_target = get_card_properties(12) 
    example_refs = [25, 2, 55, 48]  
    
    text = visual.TextStim(win, text="Here you can find an example. The card you need to classify is placed on the bottom",
                         pos=(0, 0.8), height=0.05, color='black')
    text.draw()
    
    option_positions = [(-0.45, 0.4), (-0.15, 0.4), (0.15, 0.4), (0.45, 0.4)]
    for i, num in enumerate(example_refs):
        img = visual.ImageStim(win, image=get_image_path(num), 
                             pos=option_positions[i], size=(0.2, 0.3))
        img.draw()

    target_img = visual.ImageStim(win, image=get_image_path(example_target['image_num']),
                                pos=(0, -0.3), size=(0.25, 0.35))
    target_img.draw()
    
    win.flip()
    event.waitKeys(keyList=['space'])

def show_matching_rules():
    example_target = get_card_properties(12)  
    example_refs = [25, 2, 55, 48] 
    
    text = visual.TextStim(win, text="If you want to sort it by color, you should select the first card", 
                         pos=(0, 0.8), height=0.06, color='black')
    text.draw()
    
    option_positions = [(-0.45, 0.4), (-0.15, 0.4), (0.15, 0.4), (0.45, 0.4)]
    for i, num in enumerate(example_refs):
        img = visual.ImageStim(win, image=get_image_path(num), 
                             pos=option_positions[i], size=(0.2, 0.3))
        img.draw()
    
    target_img = visual.ImageStim(win, image=get_image_path(example_target['image_num']),
                                pos=(0, -0.3), size=(0.25, 0.35))
    target_img.draw()
    
    line = visual.Line(win, start=(0, -0.2), end=(-0.45, 0.3), lineWidth=3, lineColor='red')
    line.draw()
    arrow_head = visual.Polygon(win, edges=3, radius=0.03, pos=(-0.45, 0.3), ori=45, fillColor='red', lineColor='red')
    arrow_head.draw()
    expl_text = visual.TextStim(win, text="Both are blue", pos=(0, 0), height=0.05, color='black')
    expl_text.draw()
    
    win.flip()
    event.waitKeys(keyList=['space'])
    
    text = visual.TextStim(win, text="If you want to sort it by shape, you should select the second card", 
                         pos=(0, 0.8), height=0.06, color='black')
    text.draw()
    
    for i, num in enumerate(example_refs):
        img = visual.ImageStim(win, image=get_image_path(num), 
                             pos=option_positions[i], size=(0.2, 0.3))
        img.draw()
    
    target_img.draw()
    
    line = visual.Line(win, start=(0, -0.2), end=(-0.15, 0.3), lineWidth=3, lineColor='red')
    line.draw()
    arrow_head = visual.Polygon(win, edges=3, radius=0.03, pos=(-0.15, 0.3), ori=45, fillColor='red', lineColor='red')
    arrow_head.draw()
    expl_text = visual.TextStim(win, text="Both are triangles", pos=(0, 0), height=0.05, color='black')
    expl_text.draw()
    
    win.flip()
    event.waitKeys(keyList=['space'])
    
    text = visual.TextStim(win, text="If you want to sort it by number of items, you should select the last card", 
                         pos=(0, 0.8), height=0.06, color='black')
    text.draw()
    
    for i, num in enumerate(example_refs):
        img = visual.ImageStim(win, image=get_image_path(num), 
                             pos=option_positions[i], size=(0.2, 0.3))
        img.draw()
    
    target_img.draw()
    
    line = visual.Line(win, start=(0, -0.2), end=(0.45, 0.3), lineWidth=3, lineColor='red')
    line.draw()
    arrow_head = visual.Polygon(win, edges=3, radius=0.03, pos=(0.45, 0.3), ori=-45, fillColor='red', lineColor='red')
    arrow_head.draw()
    expl_text = visual.TextStim(win, text="Both have 4 items", pos=(0, 0), height=0.05, color='black')
    expl_text.draw()
    
    win.flip()
    event.waitKeys(keyList=['space'])

def show_instructions():
    for instr in instructions:
        text = visual.TextStim(win, text=instr, height=0.06, wrapWidth=1.8, color='black')
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])
    
    show_example_trial()
    show_matching_rules()
    
    remaining_instr = [
        "You will have to figure out the classification rule by trial and error.\nFeedback will be provided after each selection\n\nPress space bar to continue",
        "The classification rule can change at any point during the task\nYou will complete a total of 128 trials\nPress space bar to continue",
        "When ready, press the space bar to start"
    ]
    for instr in remaining_instr:
        text = visual.TextStim(win, text=instr, height=0.06, wrapWidth=1.8, color='black')
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

def show_feedback(response_type):
    if response_type == 'correct':
        feedback = "Correct"
        color = 'green'
    elif response_type == 'incorrect':
        feedback = "Incorrect"
        color = 'red'
    else: 
        feedback = "No response"
        color = 'orange'
    
    text = visual.TextStim(win, text=feedback, height=0.1, color=color)
    text.draw()
    win.flip()
    core.wait(1.0)

def draw_cards(bottom_card, top_cards):
    win.flip()
    visual.TextStim(win, text="Click on the correct card", pos=(0, 0.7), height=0.05, color='black').draw()
    
    for i, card in enumerate(top_cards):
        pos = (-0.6 + i*0.4, 0.3)
        img = visual.ImageStim(win, image=get_image_path(card['image_num']), pos=pos, size=(0.25, 0.35))
        img.draw()
    
    bottom_img = visual.ImageStim(win, image=get_image_path(bottom_card['image_num']), pos=(0, -0.3), size=(0.3, 0.4))
    bottom_img.draw()
    
    click_zones = {
        'card1': visual.Rect(win, width=0.3, height=0.4, pos=(-0.6, 0.3), fillColor=None, lineColor=None),
        'card2': visual.Rect(win, width=0.3, height=0.4, pos=(-0.2, 0.3), fillColor=None, lineColor=None),
        'card3': visual.Rect(win, width=0.3, height=0.4, pos=(0.2, 0.3), fillColor=None, lineColor=None),
        'card4': visual.Rect(win, width=0.3, height=0.4, pos=(0.6, 0.3), fillColor=None, lineColor=None)
    }
    
    win.flip()
    return click_zones

def determine_correct_answer(bottom_card, top_cards):
    if current_rule == 'color':
        for i, card in enumerate(top_cards):
            if bottom_card['color'] == card['color']:
                return ['card1', 'card2', 'card3', 'card4'][i]
    elif current_rule == 'shape':
        for i, card in enumerate(top_cards):
            if bottom_card['shape'] == card['shape']:
                return ['card1', 'card2', 'card3', 'card4'][i]
    else:
        for i, card in enumerate(top_cards):
            if bottom_card['number'] == card['number']:
                return ['card1', 'card2', 'card3', 'card4'][i]
    return 'card4'

def create_bottom_card():
    image_num = random.choice(all_images)
    return get_card_properties(image_num)

def run_trial(trial_num):
    global current_rule, correct_in_row, rule_changes
    bottom_card = create_bottom_card()
    reference_image_nums = select_reference_cards(bottom_card)
    top_cards = [get_card_properties(num) for num in reference_image_nums]
    
    click_zones = draw_cards(bottom_card, top_cards)
    correct_answer = determine_correct_answer(bottom_card, top_cards)
    
    trial_data = {
        'trial_num': trial_num,
        'bottom_image': f"{bottom_card['image_num']}.jpg",
        'bottom_color': bottom_card['color'],
        'bottom_shape': bottom_card['shape'],
        'bottom_number': bottom_card['number'],
        'current_rule': current_rule,
        'response': 'no response',
        'correct': False,
        'rt': None,
        'correct_in_row': correct_in_row,
        'rule_changed': False
    }
    
    response = None
    timer = core.Clock()
    
    while timer.getTime() < 10:
        if event.getKeys(['escape']):
            win.close()
            core.quit()
        
        mouse = event.Mouse()
        if mouse.getPressed()[0]:
            mouse_pos = mouse.getPos()
            for zone in click_zones:
                if click_zones[zone].contains(mouse_pos):
                    response = zone
                    break
            if response:
                break
        
        core.wait(0.01)
    
    if response:
        trial_data['response'] = response
        if response == correct_answer:
            trial_data['correct'] = True
            correct_in_row += 1
            show_feedback('correct')
        else:
            trial_data['correct'] = False
            correct_in_row = 0
            show_feedback('incorrect')
        
        trial_data['rt'] = timer.getTime()
    else:
        show_feedback('no response')
    
    if correct_in_row >= 10:
        new_rules = [r for r in rules if r != current_rule]
        current_rule = random.choice(new_rules)
        correct_in_row = 0
        rule_changes += 1
        trial_data['rule_changed'] = True
    
    for key, value in trial_data.items():
        this_exp.addData(key, value)
    this_exp.nextEntry()

show_instructions()

for trial_num in range(1, 129):
    run_trial(trial_num)

final_text = "Thank you\nThis task is now finished\n\nPress space bar to continue"
text = visual.TextStim(win, text=final_text, height=0.08, color='black')
text.draw()
win.flip()
event.waitKeys(keyList=['space'])

win.close()