class GameManager:
    def __init__(self, player, professor):
        self.player = player
        self.professor = professor
        self.is_game_over = False
        self.time_bar = 100  # 상단 바 초기 길이
        self.is_begging = False  # 싹싹 비는 모드 여부
        self.begging_timer = 0  # 싹싹 비는 모드 타이머
        self.begging_success = 0  # 싹싹 빈 성공 횟수

    def start_begging_mode(self):
        """싹싹 비는 모드 시작"""
        self.is_begging = True
        self.begging_timer = 50  # 5초 동안 싹싹 비기
        self.begging_success = 0  # 성공 횟수 초기화

    def update_begging_mode(self, joystick):
        """싹싹 비는 모드 업데이트"""
        if self.begging_timer > 0:
            self.begging_timer -= 1
            # 조이스틱 움직임 감지
            if not joystick.button_L.value or not joystick.button_R.value:
                self.begging_success += 1
                if self.begging_success >= 15:  # 목표 달성
                    self.is_begging = False  # 싹싹 비는 모드 종료
                    return True  # 용서받음
        else:
            self.is_game_over = True  # 시간 초과로 게임 오버
        return False  # 아직 목표 달성 안 됨

    def update(self, current_stage):
        """게임 상태 업데이트"""
        if self.is_begging:
            return  # 싹싹 비는 모드 중에는 핑크색 바 감소 중단

        # 일반 게임 모드에서만 시간 감소
        if self.time_bar > 0:
            decrement = {1: 0.15, 2: 0.2, 3: 0.28, 4: 0.35, 5: 0.38}
            self.time_bar -= decrement.get(current_stage, 0.7)
            self.time_bar = max(0, self.time_bar)  # 시간 바가 음수가 되지 않도록 보정

        # 시간 초과로 게임 오버
        if self.time_bar <= 0:
            self.is_game_over = True