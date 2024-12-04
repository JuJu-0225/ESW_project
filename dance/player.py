class Player:
    def __init__(self):
        self.is_dancing = False
        self.score = 0
        self.position = (85, 150, 135, 200)  # 플레이어 위치 (x1, y1, x2, y2)

    def update_state(self, dancing, current_stage):
        """플레이어의 상태를 업데이트"""
        self.is_dancing = dancing
        if dancing:
            # 스테이지에 따라 점수 증가 속도 조정
            self.score += current_stage + 1