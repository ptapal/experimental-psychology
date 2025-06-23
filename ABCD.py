from psychopy import visual, core, event, gui
import os
import random
import time
import pandas as pd

win = visual.Window([1024, 768], fullscr=False, units='pix', color='white')

GREEN = '#00FF00'
RED = '#FF0000'
BLACK = '#000000'
WHITE = '#FFFFFF'

IMAGE_SIZE = (120, 120)
FRAME_SIZE = (130, 130)
FRAME_COLOR = BLACK
TEXT_HEIGHT = 30
TEXT_COLOR = BLACK

IMAGE_POSITIONS = [
    (-225, 150), (-75, 150), (75, 150), (225, 150),  
    (-225, -100), (-75, -100), (75, -100), (225, -100)  
]

results = []

def show_text(text, advance_key='space', pos=(0, 0)):
    """Display centered text and wait for keypress"""
    text_stim = visual.TextStim(win, text=text, height=TEXT_HEIGHT, 
                              color=TEXT_COLOR, wrapWidth=900, pos=pos)
    text_stim.draw()
    win.flip()
    event.waitKeys(keyList=[advance_key])

def show_feedback(is_correct, duration=1.0):
    """Show feedback for specified duration (practice only)"""
    feedback = "Correct" if is_correct else "Incorrect"
    color = GREEN if is_correct else RED
    feedback_stim = visual.TextStim(win, text=feedback, color=color, height=40)
    feedback_stim.draw()
    win.flip()
    core.wait(duration)

def load_image(image_num):
    """Try to load image, return None if not found"""
    img_path = f"Images/image{image_num}.jpeg"
    if os.path.exists(img_path):
        return img_path
    print(f"Image not found: {img_path}")
    return None

def create_trial_display(question_images, answer_images, correct_num=None):
    """Create trial display with 3+1 top and 4 bottom images"""
    elements = []
    clickable_elements = []
    
    top_labels = ['A', 'B', 'C', 'D']
    label_offset = -100 
    
    for i in range(4):
        pos = IMAGE_POSITIONS[i]
        frame = visual.Rect(win, width=FRAME_SIZE[0], height=FRAME_SIZE[1],
                            pos=pos, lineColor=FRAME_COLOR, lineWidth=3)

        label_pos = (pos[0], pos[1] + label_offset)
        label = visual.TextStim(win, text=top_labels[i], pos=label_pos, height=0.05, color='black')

        if i < len(question_images) and question_images[i]:
            img_path = load_image(question_images[i])
            if img_path:
                image = visual.ImageStim(win, image=img_path, size=IMAGE_SIZE, pos=pos)
                elements.append(('image', frame, image, label, question_images[i]))
            else:
                elements.append(('blank', frame, None, label, None))
        else:
            elements.append(('blank', frame, None, label, None))
    
    correct_pos = -1
    
    for i in range(4):
        pos = IMAGE_POSITIONS[4 + i]
        frame = visual.Rect(win, width=FRAME_SIZE[0], height=FRAME_SIZE[1],
                            pos=pos, lineColor=FRAME_COLOR, lineWidth=3)

        if i < len(answer_images) and answer_images[i]:
            img_path = load_image(answer_images[i])
            if img_path:
                image = visual.ImageStim(win, image=img_path, size=IMAGE_SIZE, pos=pos)
                elements.append(('answer', frame, image, None, answer_images[i]))
                is_correct = (answer_images[i] == correct_num)
                if is_correct:
                    correct_pos = 4 + i
                clickable_elements.append((frame, image, is_correct))
            else:
                elements.append(('blank', frame, None, None, None))
        else:
            elements.append(('blank', frame, None, None, None))

    return elements, clickable_elements, correct_pos
    
def show_illustration():
    """Show the illustration example with proper spacing"""
    text = visual.TextStim(win, 
                         text="In this example, cat (A) is to kitten (B), as Dog (C) is to..? ",
                         pos=(0, 300), 
                         height=TEXT_HEIGHT, 
                         color=TEXT_COLOR)
    
    question_images = [1, 2, 3] 
    answer_images = [5, 7, 6, 4] 
    elements, _, _ = create_trial_display(question_images, answer_images, 4)
    
    text.draw()
    for elem_type, frame, image, label, num in elements:
        frame.draw()
        if image:
            image.draw()
        if label:
            label.draw()
    
    puppy_label = visual.TextStim(win, text="puppy (D)", pos=(225, -200), 
                                height=24, color=TEXT_COLOR)
    puppy_label.draw()
    
    win.flip()
    event.waitKeys(keyList=['space'])

def run_color_discrimination_task():
    color_pairs = [
        ('#0000FF', '#0000FF'),
        ('#888888', '#0000FF'), ('#888888', '#FFFF00'), ('#888888', '#00FF00'),
        ('#888888', '#AA5500'), ('#888888', '#FF00FF'), ('#888888', '#FF0000'),
        ('#0000FF', '#FFFF00'), ('#0000FF', '#00FF00'), ('#0000FF', '#AA5500'),
        ('#0000FF', '#FF00FF'), ('#0000FF', '#FF0000'), ('#0000FF', '#0000FF'),
        ('#FFFF00', '#FFFF00'), ('#FFFF00', '#00FF00'), ('#FFFF00', '#AA5500'),
        ('#FFFF00', '#FF00FF'), ('#FFFF00', '#FF0000'),
        ('#00FF00', '#00FF00'), ('#00FF00', '#AA5500'), ('#00FF00', '#FF00FF'),
        ('#00FF00', '#FF0000'),
        ('#AA5500', '#AA5500'), ('#AA5500', '#FF00FF'), ('#AA5500', '#FF0000'),
        ('#FF00FF', '#FF00FF'), ('#FF00FF', '#FF0000'),
        ('#FF0000', '#FF0000')
    ]
    
    random.shuffle(color_pairs)
    
    same_text = visual.TextStim(win, text="Same", pos=(-150, -200), height=30, color='black')
    diff_text = visual.TextStim(win, text="Different", pos=(150, -200), height=30, color='black')
    
    for color1, color2 in color_pairs:
        square1 = visual.Rect(win, width=150, height=150, pos=(-150, 0), fillColor=color1, lineColor=None)
        square2 = visual.Rect(win, width=150, height=150, pos=(150, 0), fillColor=color2, lineColor=None)
        
        square1.draw()
        square2.draw()
        same_text.draw()
        diff_text.draw()
        win.flip()
        
        mouse = event.Mouse()
        response = None
        mouse_down_pos = None
        trial_clock = core.Clock()
        
        while response is None:
            mouse_pressed = mouse.getPressed()[0]
            mouse_pos = mouse.getPos()
            
            if mouse_pressed and mouse_down_pos is None:
                mouse_down_pos = mouse_pos
                mouse_down_time = trial_clock.getTime()
            
            elif not mouse_pressed and mouse_down_pos is not None:
                reaction_time = (trial_clock.getTime() - mouse_down_time) * 1000
                if same_text.contains(mouse_pos) and same_text.contains(mouse_down_pos):
                    response = 'same'
                elif diff_text.contains(mouse_pos) and diff_text.contains(mouse_down_pos):
                    response = 'different'
                
                mouse_down_pos = None 
            
            core.wait(0.02)
        
        correct_answer = 'same' if color1 == color2 else 'different'
        results.append({
            'task': 'color_discrimination',
            'color1': color1,
            'color2': color2,
            'response': response,
            'is_correct': response == correct_answer,
            'reaction_time_ms': reaction_time
        })
        
def run_trial(question_images, answer_images, correct_num, is_practice=False, trial_type="main"):
    """Run a single trial with proper click handling"""
    elements, clickable_elements, _ = create_trial_display(question_images, answer_images, correct_num)
    
    instruction = visual.TextStim(win, text="Click on the correct answer", 
                                pos=(0, 250), height=TEXT_HEIGHT)
    
    instruction.draw()
    for elem_type, frame, image, label, *_ in elements:
        frame.draw()
        if image:
            image.draw()
        if label:
            label.draw()
    win.flip()
    
    mouse = event.Mouse()
    trial_clock = core.Clock()
    response_made = False
    mouse_down_pos = None
    mouse_down_time = 0
    
    while True:
        current_time = trial_clock.getTime()
        if not is_practice and current_time > 15:
            if not response_made:
                results.append({
                    'trial_type': trial_type,
                    'question_images': question_images,
                    'answer_images': answer_images,
                    'correct_answer': correct_num,
                    'selected_answer': None,
                    'is_correct': False,
                    'reaction_time_ms': 15000,
                    'timeout': True
                })
            return False
        
        mouse_pressed = mouse.getPressed()[0]
        mouse_pos = mouse.getPos()
        
        if mouse_pressed and mouse_down_pos is None:
            mouse_down_pos = mouse_pos
            mouse_down_time = current_time
        
        elif not mouse_pressed and mouse_down_pos is not None:
            for frame, image, is_correct in clickable_elements:
                frame_contains_press = frame.contains(mouse_down_pos)
                image_contains_press = image and image.contains(mouse_down_pos)
                frame_contains_release = frame.contains(mouse_pos)
                image_contains_release = image and image.contains(mouse_pos)
                
                if (frame_contains_press or image_contains_press):
                    if (frame_contains_release or image_contains_release):
                        reaction_time = (current_time - mouse_down_time) * 1000
                        response_made = True
                        if not is_practice:
                            results.append({
                                'trial_type': trial_type,
                                'question_images': question_images,
                                'answer_images': answer_images,
                                'correct_answer': correct_num,
                                'selected_answer': answer_images[clickable_elements.index((frame, image, is_correct))],
                                'is_correct': is_correct,
                                'reaction_time_ms': reaction_time,
                                'timeout': False
                            })
                        if is_practice:
                            show_feedback(is_correct)
                        mouse_down_pos = None  
                        return is_correct
            mouse_down_pos = None
        
        core.wait(0.02)

def save_results(participant_info):
    """Save results to a CSV file"""
    if not results:
        return

    df = pd.DataFrame(results)

    os.makedirs("data", exist_ok=True)

    filename = f"data/results_{participant_info['Patient ID']}_session{participant_info['Session']}.csv"

    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")
    
def main():
    participant_info = {'Patient ID': '', 'Session': ''}
    info_dlg = gui.DlgFromDict(dictionary=participant_info, title='Participant Information')
    if not info_dlg.OK:
        core.quit()
    
    show_text("In this task, you will analyze pairs of concepts to determine the relationship between them.\nFor each question, you will be presented with an analogy in the A:B::C:D format")
    show_text("Each analogy follows this pattern: A is to B as C is to D.\nThis means that the relationship between A and B should be the same as the relationship between C and D")
    
    show_illustration()
    show_text("For you to get familiar with the procedure, we will do two practice trials.\nThe task will start afterwards")
    
    practice_sets = [
        {'questions': [8, 9, 10], 'answers': [11, 12, 13, 14], 'correct': 11},
        {'questions': [14, 18, 16], 'answers': [19, 17, 15, 20], 'correct': 17}
    ]
    
    for trial in practice_sets[:2]:  
        while True:
            if run_trial(trial['questions'], trial['answers'], trial['correct'], is_practice=True):
                break

    show_text("Now the actual task will begin. You will no longer receive feedback.")
    
    main_trials = [
        {'questions': [22,23,24], 'answers': [26,27,18,25], 'correct': 25},
        {'questions': [32,28,29], 'answers': [31,14,30,33], 'correct': 33},
        {'questions': [34,35,1], 'answers': [39,37,36,38], 'correct': 36},
        {'questions': [40,41,42], 'answers': [46,44,45,43], 'correct': 43},
        {'questions': [47,48,49], 'answers': [50,52,53,51], 'correct': 50},
        {'questions': [6,57,55], 'answers': [54,56,58,59], 'correct': 59},
        {'questions': [49,60,62], 'answers': [63,65,64,61], 'correct': 61},
        {'questions': [66,67,3], 'answers': [15,69,5,70], 'correct': 69},
        {'questions': [76,71,75], 'answers': [51,74,73,72], 'correct': 72},
        {'questions': [80,79,20], 'answers': [78,77,16,7], 'correct': 78},
        {'questions': [84,86,85], 'answers': [82,39,83,81], 'correct': 83},
        {'questions': [88,89,86], 'answers': [77,7,90,87], 'correct': 87}
    ]
    
    for trial in main_trials:
        run_trial(trial['questions'], trial['answers'], trial['correct'], is_practice=False, trial_type="main")
    
    show_text("Next, you will see pairs of colored squares. Your task is to determine if they are the same or different.")
    show_text("Click 'Same' if the colors are identical, or 'Different' if they are not.")
    run_color_discrimination_task()
    
    show_text("In this task, you will continue analyzing pairs of concepts to determine the relationship between them, following the A:B::C:D format")
    show_text("Differently to previous trials, this time the objects will be colored")
    show_text("For you to get familiar with the procedure, we will do three practice trials. The task will start afterwards")
    
    col_practice_sets = [
        {'questions': [94, 95, 96], 'answers': [99, 98, 97, 100], 'correct': 97},
        {'questions': [102, 103, 104], 'answers': [107, 101, 105, 106], 'correct': 105},
        {'questions': [110,109,108], 'answers': [111,112,113,114], 'correct': 111}
    ]
    
    for trial in col_practice_sets[:3]:  # Only 2 practice trials
        while True:
            if run_trial(trial['questions'], trial['answers'], trial['correct'], is_practice=True):
                break
                
    show_text("Now the task will start. You will no longer receive feedback on your answers")
    color_trials = [
        {'questions': [116,117,118], 'answers': [119,121,120,115], 'correct': 120},
        {'questions': [122,123,127], 'answers': [126,125,124,128], 'correct': 128},
        {'questions': [129,130,94], 'answers': [134,133,131,132], 'correct': 131},
        {'questions': [137,138,139], 'answers': [140,136,141,135], 'correct': 140},
        {'questions': [148,142,143], 'answers': [146,144,145,147], 'correct': 144},
        {'questions': [151,150,152], 'answers': [154,153,155,149], 'correct': 153},
        {'questions': [156,157,158], 'answers': [161,159,160,162], 'correct': 159},
        {'questions': [167,166,164], 'answers': [165,163,168,169], 'correct': 165},
        {'questions': [171,170,173], 'answers': [172,175,176,174], 'correct': 174},
        {'questions': [183,182,181], 'answers': [178,179,180,177], 'correct': 180},
        {'questions': [190,189,188], 'answers': [187,186,185,184], 'correct': 187},
        {'questions': [197,196,195], 'answers': [193,194,192,191], 'correct': 194}
    ]
    
    for trial in color_trials:
        run_trial(trial['questions'], trial['answers'], trial['correct'], is_practice=False, trial_type="color")
    
    save_results(participant_info)
    
    show_text("Task complete! Thank you for participating.")
    win.close()

if __name__ == '__main__':
    main()
    
    save_results(participant_info)
    
    show_text("Task complete! Thank you for participating.")
    win.close()
    