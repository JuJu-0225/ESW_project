import random
import time

class Professor:
    def __init__(self):
        self.is_watching = False
        self.watch_timer = 0  # 감시 상태 지속 시간
        self.last_watch_time = 0  # 마지막으로 뒤돌아본 시간
        self.grace_period = 0.3  # 안전 시간 (0.3초)
        self.position = (90, 50, 140, 100)  # 교수님 위치 (x1, y1, x2, y2)

    def update_state(self, current_stage):
        """교수님의 상태를 단계별로 업데이트"""
        if self.watch_timer <= 0:
            self.is_watching = random.choice([True, False])
            if self.is_watching:
                self.last_watch_time = time.time()  # 교수님이 돌아본 시간 기록
            # 단계별 최소 및 최대 감시 시간 설정
            stage_timer = {
                1: (2, 3),
                2: (1, 3),
                3: (1, 3),
                4: (1, 3),
                5: (1, 3),
            }
            min_time, max_time = stage_timer.get(current_stage, (1, 1))
            self.watch_timer = random.randint(min_time, max_time)
        else:
            self.watch_timer -= 1