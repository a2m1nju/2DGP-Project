from pico2d import *
import game_framework
import play_mode

BGM_DURATION = 23.0

def init():
    global images1, images2, current_frame, phase, frame_timer, total_time, bgm
    global background_image, intro2_delay
    global font, intro_msg_lines, intro2_msg_lines
    global text_visible_count, text_timer
    global text2_visible_count, text2_timer

    background_image = load_image('./배경/인트로배경.png')

    images1 = []
    for i in range(1, 300):
        filename = f'./배경/인트로/frame_{i:04d}.jpg'
        images1.append(load_image(filename))

    images2 = []
    for i in range(1, 78):
        filename = f'./배경/인트로2/frame_{i:04d}.jpg'
        images2.append(load_image(filename))

    current_frame = 0
    phase = 1
    frame_timer = 0.0
    total_time = 0.0

    try:
        font = load_font('DungGeunMo.ttf', 25)
    except:
        font = load_font('Arial.ttf', 30)

    intro_msg_lines = [
        "오늘도 심연교통공사를",
        "이용해 주셔서 감사합니다.",
        "고객의 안전을 가장 먼저",
        "생각하며 쾌적하고 편안한",
        "지하철이 되도록",
        "최선을 다하겠습니다."
    ]
    text_visible_count = 0
    text_timer = 0.0

    intro2_msg_lines = [
        "⫷⫸⩜⩚⩫⩳⪦ÑøÜåŠïÊžÓæÍûÇ",
        "⫕žÆïÒâÉšÜøÏáÓëÛ⫝⪹⪦⩚",
        "ŠéÛï⫙⪍čÍÿØëŠúÉ⫙⪩⩳",
        "⪬šÊøÑîÉžäØ⩳⫗⫽ŠéÛï",
        "⪬ÅëÏûÓášÊøÑîÉž⩜⫽⫥⪙",
        "îžËåÓçíÅœÏ⪮⫽⪍⫚žÍäÆš",
        "ØäñÛšÉôž⫣⩱⫽⫧ñóä",
        "⪚äñÛšÉôžÅÏëÚšéÓæÎŠ"
    ]
    text2_visible_count = 0
    text2_timer = 0.0

    remaining_time = BGM_DURATION - 9.0
    if remaining_time > 0 and len(images2) > 0:
        intro2_delay = remaining_time / len(images2)
    else:
        intro2_delay = 0.04

    try:
        bgm = load_music('./음악/심연교통공사2.mp3')
    except:
        bgm = load_music('./음악/심연교통공사.wav')

    bgm.set_volume(30)
    bgm.play(1)


def finish():
    global images1, images2, bgm, background_image, font
    del images1
    del images2
    del bgm
    del background_image
    del font

def update():
    global current_frame, frame_timer, total_time, phase
    global text_visible_count, text_timer
    global text2_visible_count, text2_timer

    INTRO1_DELAY = 0.04
    TEXT_SPEED = 0.15
    TEXT_SPEED2 = 0.08

    dt = game_framework.frame_time
    frame_timer += dt
    total_time += dt

    if phase == 1:
        while frame_timer >= INTRO1_DELAY:
            frame_timer -= INTRO1_DELAY
            current_frame = (current_frame + 1) % len(images1)

        text_timer += dt
        while text_timer >= TEXT_SPEED:
            text_timer -= TEXT_SPEED
            text_visible_count += 1

        if total_time >= 11.0:
            phase = 2
            current_frame = 0
            frame_timer = 0.0
            text2_timer = 0.0
            text2_visible_count = 0



    elif phase == 2:
        while frame_timer >= intro2_delay:
            frame_timer -= intro2_delay
            current_frame = (current_frame + 1) % len(images2)

        text2_timer += dt

        while text2_timer >= TEXT_SPEED2:
            text2_timer -= TEXT_SPEED2
            text2_visible_count += 1
        if total_time >= BGM_DURATION:

            game_framework.change_mode(play_mode)


def draw():
    clear_canvas()

    background_image.draw(800, 300, 1600, 600)

    if phase == 1:
        images1[current_frame].draw(800, 300, 903, 600)

        start_x = 15
        start_y = 550
        line_height = 40

        temp_count = text_visible_count

        for i, line in enumerate(intro_msg_lines):
            if temp_count > 0:
                count_in_this_line = min(len(line), temp_count)
                text_to_draw = line[:count_in_this_line]
                font.draw(start_x, start_y - (i * line_height), text_to_draw, (255, 255, 255))
                temp_count -= len(line)
            else:
                break


    elif phase == 2:
        idx = current_frame % len(images2)

        images2[idx].draw(800, 300, 903, 600)

        start_x = 1280
        start_y = 550
        line_height = 35
        temp_count = text2_visible_count

        for i, line in enumerate(intro2_msg_lines):
            if temp_count > 0:
                count_in_this_line = min(len(line), temp_count)
                text_to_draw = line[:count_in_this_line]
                font.draw(start_x, start_y - (i * line_height), text_to_draw, (255, 0, 0))
                temp_count -= len(line)
            else:
                break

    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.change_mode(play_mode)