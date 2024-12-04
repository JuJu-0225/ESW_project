from PIL import Image, ImageDraw, ImageFont
import time
import random
from player import Player
from professor import Professor
from joystick import Joystick
from gamemanager import GameManager


def calculate_stage(score):
    """점수에 따라 단계 계산"""
    return min(score // 100 + 1, 5)


def load_gif_frames(file_path, frame_size):
    """GIF 파일의 모든 프레임을 로드하고 크기를 조정"""
    gif = Image.open(file_path)
    frames = []
    try:
        while True:
            frame = gif.copy().resize(frame_size).convert("RGBA")  # RGBA로 변환
            frames.append(frame)
            gif.seek(gif.tell() + 1)  # 다음 프레임으로 이동
    except EOFError:
        pass  # GIF의 마지막 프레임에 도달
    return frames


def begging_mode(joystick, font, current_stage):
    """싹싹 비는 모드 구현"""
    start_time = time.time()
    max_time = 5  # 5초 제한
    required_begs = 15
    begs = 0
    sorry_background = Image.open("sorry.png").resize((joystick.width, joystick.height)).convert("RGBA")

    while True:
        elapsed_time = time.time() - start_time
        remaining_time = max(0, max_time - elapsed_time)

        # 조이스틱 입력 감지 (양옆 움직임)
        if not joystick.button_L.value or not joystick.button_R.value:
            begs += 1

        # 배경 렌더링
        image = sorry_background.copy()
        draw = ImageDraw.Draw(image)

        # 남은 시간 및 빈 횟수 표시
        draw.text((joystick.width - 160, 10), f"Time: {remaining_time:.1f}s", fill=(255, 255, 255), font=font)
        draw.text((joystick.width - 160, 40), f"Begs: {begs}/{required_begs}", fill=(255, 255, 255), font=font)

        # 디스플레이 출력
        joystick.disp.image(image)
        time.sleep(0.1)

        # 용서 조건 달성
        if begs >= required_begs:
            # 용서 메시지 출력
            draw.text((joystick.width // 2 - 80, joystick.height // 2), "I will forgive you!", fill=(0, 255, 0), font=font)
            joystick.disp.image(image)
            time.sleep(2)  # 2초 동안 메시지 표시
            return True

        # 시간 초과
        if remaining_time <= 0:
            return False


def main():
    while True:  # 무한 루프로 게임 재시작 가능
        # 초기화
        joystick = Joystick()
        player = Player()
        professor = Professor()
        game_manager = GameManager(player, professor)

        # 배경 및 UI 요소 이미지 로드
        background = Image.open("background.png").resize((joystick.width, joystick.height)).convert("RGBA")
        bar_image = Image.open("bar.png").resize((200, 20)).convert("RGBA")
        end_background = Image.open("end.png").resize((joystick.width, joystick.height)).convert("RGBA")
        success_background = Image.open("success.png").resize((joystick.width, joystick.height)).convert("RGBA")  # 성공 배경
        pause_background = Image.open("pause.png").resize((joystick.width, joystick.height)).convert("RGBA")  # 일시정지 배경
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)

        # GIF 프레임 로드
        player_frame_size = (90, 90)  # 플레이어 크기를 90x90으로 설정
        player_frames = load_gif_frames("player.gif", player_frame_size)
        player_dancing_frames = load_gif_frames("player_dancing.gif", player_frame_size)
        player_frame_index = 0

        # 초기 스테이지 설정
        current_stage = 1

        game_cleared = False  # 게임 클리어 여부
        paused = False  # 일시정지 상태

        while not game_manager.is_game_over and not game_cleared:
            # 버튼 #6 확인: 일시정지
            if not joystick.button_B.value:  # 버튼 #6이 눌렸을 때
                paused = not paused  # 일시정지 토글
                if paused:
                    # 일시정지 배경화면 표시
                    image = pause_background.copy()
                    draw = ImageDraw.Draw(image)
                    draw.text((joystick.width // 2 - 50, joystick.height // 2), "Paused", fill=(255, 0, 0), font=font)
                    joystick.disp.image(image)
                    while paused:
                        time.sleep(0.1)
                        if not joystick.button_B.value:  # 버튼 #6 다시 눌리면 일시정지 해제
                            paused = False
                            break

            # 입력 처리
            command = {'dancing': False}
            if not joystick.button_A.value:  # 버튼 #5 확인
                command['dancing'] = True

            # 플레이어 및 교수님 상태 업데이트
            player.update_state(command['dancing'], current_stage)
            professor.update_state(current_stage)

            # 걸렸을 때 안전 시간 체크
            if professor.is_watching and player.is_dancing:
                current_time = time.time()
                if current_time - professor.last_watch_time > professor.grace_period:
                    # 안전 시간 이후 싹싹 비는 모드 진입
                    if begging_mode(joystick, font, current_stage):
                        professor.is_watching = False  # 용서받고 계속 진행
                    else:
                        game_manager.is_game_over = True  # 시간 초과로 게임 종료
                        break

            # 스테이지 변경 확인
            new_stage = calculate_stage(player.score)
            if new_stage > current_stage:
                current_stage = new_stage
                # 스테이지 변경 메시지 표시
                image = background.copy()
                draw = ImageDraw.Draw(image)
                draw.text((joystick.width // 2 - 70, joystick.height // 2), f"Stage {current_stage}", fill=(0, 255, 0), font=font)
                joystick.disp.image(image)
                time.sleep(2)  # 2초 동안 메시지 표시

            # **GameManager 업데이트 호출 (핑크색 바 감소)**
            game_manager.update(current_stage)

            # 게임 클리어 조건 확인
            if player.score >= 500:
                game_cleared = True  # 게임 클리어 상태로 전환
                break

            # 화면 렌더링
            image = background.copy()
            draw = ImageDraw.Draw(image)

            # 상단 바
            bar_width = int(game_manager.time_bar * 2)
            image.paste(bar_image.crop((0, 0, bar_width, 20)), (20, 10))

            # 플레이어 애니메이션
            if player.is_dancing:
                if player_dancing_frames:
                    player_image = player_dancing_frames[player_frame_index % len(player_dancing_frames)]
                else:
                    player_image = player_frames[player_frame_index % len(player_frames)]
            else:
                player_image = player_frames[player_frame_index % len(player_frames)]

            player_frame_index = (player_frame_index + 1) % max(len(player_frames), len(player_dancing_frames))

            # RGBA 변환 (투명도 문제 해결)
            player_image = player_image.convert("RGBA")
            image.paste(player_image, (player.position[0], player.position[1]), player_image)

            # 교수님 이미지 (뒤를 볼 때는 춤 가능, 앞을 볼 때는 걸림)
            professor_image_path = "professor_back.png" if not professor.is_watching else "professor_front.png"
            professor_image = Image.open(professor_image_path).resize((80, 80)).convert("RGBA")
            image.paste(professor_image, (professor.position[0], professor.position[1]), professor_image)

            # 점수 표시
            draw.text((10, 10), f"Score: {player.score}", fill=(0, 0, 0), font=font)

            # 디스플레이 출력
            joystick.disp.image(image)
            time.sleep(0.1)

        if game_cleared:
            # 성공 배경 화면 표시
            image = success_background.copy()
            draw = ImageDraw.Draw(image)
            draw.text((joystick.width // 2 - 100, joystick.height // 2 - 20), "SUCCESS!", fill=(0, 255, 0), font=font)
            draw.text((joystick.width // 2 - 100, joystick.height // 2 + 20), "Press A to Replay", fill=(0, 0, 0), font=font)
            joystick.disp.image(image)

            # 게임 재시작 대기
            while joystick.button_A.value:  # A 버튼 대기
                time.sleep(0.1)

        elif game_manager.is_game_over:
            # 게임 오버 화면 표시
            image = end_background.copy()
            draw = ImageDraw.Draw(image)
            draw.text((joystick.width // 2 - 70, joystick.height // 2), "Game Over", fill=(255, 0, 0), font=font)
            draw.text((joystick.width // 2 - 70, joystick.height // 2 + 20), f"Score: {player.score}", fill=(255, 0, 0), font=font)
            draw.text((joystick.width // 2 - 70, joystick.height // 2 + 40), "Press A to Restart", fill=(0, 0, 0), font=font)
            joystick.disp.image(image)

            # A 버튼 대기
            while joystick.button_A.value:
                time.sleep(0.1)


if __name__ == "__main__":
    main()