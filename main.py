from pumpkinpipe.hand import HandDetector
import cv2
import xarm
from time import monotonic

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min



UPDATE = 0.15

arm = xarm.Controller('USB')

# Open webcam
cap = cv2.VideoCapture(0)

WIDTH = 1280
HEIGHT = 720

cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

# Create detector
hand_detector = HandDetector(max_hands=1)
start_time = monotonic()
openness = 500
current_openness = openness + 100
max_open = 0.7
min_open = 0.6
current_angle = 600
angle = 500
hand_open = False

arm.setPosition(2, 500, wait=True)
while True:
    elapsed = monotonic() - start_time

    # Read frame
    success, frame = cap.read()

    # Flip for mirror view
    frame = cv2.flip(frame, 1)

    # Detect hands
    hands = hand_detector.find_hands(frame)

    # Draw debug info for each hand
    for hand in hands:
        hand.draw()
        hand_open = sum(hand.flags) >=3
        hand_x = hand.center[0]
        hand_openness = hand.landmark_distance(4, 8) / hand.landmark_distance(9, 0)
        hand_x = max(min(hand_x, 1100), 180)
        angle = map_range(hand_x, 280, 1000, 325, 675)
        if hand_open:
            openness = 1000
        else:
            openness = 0
        cv2.putText(
            frame,  # Image to draw on
            str(current_angle),  # Text to write
            (50, 50),  # Position of the text
            cv2.FONT_HERSHEY_SIMPLEX,  # Font to render text as
            1,  # Scale (size)
            (255, 255, 255),  # Color in BGR format
            2  # Line thickness
        )
    if elapsed > UPDATE:
        if abs(current_openness - openness) > 75:
            current_openness = int(openness)
            arm.setPosition(1, 1000 - current_openness)
        if abs(current_angle - angle)  > 75:
            current_angle = int(angle)
            for i in range(3, 6):
                if i % 2 == 0:
                    arm.setPosition(i, 1000 - current_angle)
                else:
                    arm.setPosition(i, current_angle)
        start_time = monotonic()
    # Show result
    cv2.imshow("Debug Example", frame)

    # Exit if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Exit if the window is manually closed
    if cv2.getWindowProperty("Debug Example", cv2.WND_PROP_VISIBLE) < 1:
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()