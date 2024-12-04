from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789
from digitalio import DigitalInOut
import board

# 디스플레이 초기화
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D24)
BAUDRATE = 24000000

spi = board.SPI()
disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# 백라이트 켜기
backlight = DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True

# 화면에 단색 출력 테스트
image = Image.new("RGB", (disp.width, disp.height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, disp.width, disp.height), fill=(255, 0, 0))  # 빨간색 출력
disp.image(image)