from pumpkinpipe.hand import HandDetector
import cv2
import xarm
from time import monotonic, sleep
import math
def radians_yaw(p1, p2):
    dx = p2[0] - p1[0]
    dz = p2[2] - p1[2]
    return math.atan2(dz, dx)
def radians_tilt(p1, p2):
    dy = -(p2[1] - p1[1])
    dz = p2[2] - p1[2]
    return math.atan2(dy, dz)
def get_tilt(p1, p2):
    degrees_angle = math.degrees(radians_tilt(p1, p2))
    return 360 - ((degrees_angle + 90) % 360)
def get_yaw(p1, p2):
    degrees_angle = math.degrees(radians_yaw(p1, p2))
    return degrees_angle + 360
def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
UPDATE = 0.15
arm = xarm.Controller('USB')
cap = cv2.VideoCapture(0)
WIDTH = 1280
HEIGHT = 720
EDGE = 200
RIGHT = 100
LEFT = 900
LEFT_WRIST = 16
RIGHT_WRIST = 15
LEFT_SHOULDER = 14
RIGHT_SHOULDER = 13
UP = 525
DOWN = 315
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
hand_detector = HandDetector(max_hands=1)
start_time = monotonic()
openness = 500
current_openness = 500
current_angle = 500
angle = 500
hand_open = False
upness = 500
current_upness = 500
side = "Left"
tilt = 500
for i in range(7):
    arm.setPosition(i, 500)
sleep(1)
while True:
    elapsed = monotonic() - start_time
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    hands = hand_detector.find_hands(frame)
    for hand in hands:
        side = hand.side
        hand.draw()
        hand_open = sum(hand.flags) >=3
        if hand_open:
            openness = 1000
        else:
            openness = 300
        middle = hand.landmarks[9]
        hand_angle = int(get_yaw(hand.wrist, middle) - 180)
        hand_angle = min(145, max(45, hand_angle))
        angle = map_range(hand_angle, 45, 145, LEFT, RIGHT)
        hand_tilt = int(get_tilt(hand.wrist, middle))
        hand_tilt = min(187, max(95, hand_tilt))
        tilt = map_range(hand_tilt, 95, 187, DOWN, UP)
    if elapsed > UPDATE:
        if abs(current_openness - openness) > 75:
            current_openness = int(openness)
            arm.setPosition(1, 1000 - current_openness)
        if abs(current_angle - angle)  > 25:
            current_angle = int(angle)
            arm.setPosition(6, current_angle)
        if abs(current_upness - tilt) > 5:
            current_upness = int(tilt)
            for i in range(3, 6):
                if i % 2 == 0:
                    arm.setPosition(i, current_upness)
                else:
                    arm.setPosition(i, 1000 - current_upness)
        start_time = monotonic()
    cv2.imshow("Debug Example", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty("Debug Example", cv2.WND_PROP_VISIBLE) < 1:
        break
cap.release()
cv2.destroyAllWindows()