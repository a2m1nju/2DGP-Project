from pico2d import *
import game_framework
import game_world
import os


image_frames = []
current_frame_index = 0
frame_count = 88
frame_delay = 0.05
frame_timer = 0.0
background_image = None
effect_sound = None
total_timer = 0.0
TOTAL_DURATION = frame_count * frame_delay


def init():
    global image_frames, background_image, effect_sound
    global current_frame_index, frame_timer, total_timer

    game_world.clear()
    image_frames = []

    try:
        effect_sound = load_wav('./음악/팡파레.mp3')
        effect_sound.set_volume(50)
        effect_sound.play()
    except:
        print("효과음 로드 실패")

    try:
        background_image = load_image('./배경/정왕역배경.png')
    except:
        background_image = None
        print("배경 이미지 로드 실패")

    base_path = './배경/정왕역'

    for i in range(1, frame_count + 1):
        filename = f'frame_{i:04d}.jpg'
        full_path = os.path.join(base_path, filename)

        try:
            image = load_image(full_path)
            image_frames.append(image)
        except Exception as e:
            print(f"이미지 로드 실패: {full_path}, {e}")
            image_frames = []
            break

    current_frame_index = 0
    frame_timer = 0.0
    total_timer = 0.0

    if not image_frames:
        import gameclear_mode
        game_framework.change_mode(gameclear_mode)


def finish():
    global image_frames
    image_frames = []


def update():
    global current_frame_index, frame_timer, total_timer

    frame_timer += game_framework.frame_time
    total_timer += game_framework.frame_time

    if frame_timer >= frame_delay:
        frame_timer = 0.0
        current_frame_index = (current_frame_index + 1) % len(image_frames)

    if total_timer >= TOTAL_DURATION:
        import gameclear_mode
        game_framework.change_mode(gameclear_mode)
        return


def draw():
    clear_canvas()

    if background_image:
        background_image.draw(800, 300, 1600, 600)

    if image_frames:
        image_frames[current_frame_index].draw(800, 300, 900, 600)

    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            import gameclear_mode
            game_framework.change_mode(gameclear_mode)