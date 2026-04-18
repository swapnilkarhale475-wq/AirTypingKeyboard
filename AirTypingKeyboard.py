import cv2
import mediapipe as mp
import pyautogui
import winsound
import time

# Camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Hand Detector
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mpDraw = mp.solutions.drawing_utils

# Keyboard Layout
keys = [["Q","W","E","R","T","Y","U","I","O","P"],
        ["A","S","D","F","G","H","J","K","L"],
        ["Z","X","C","V","B","N","M"],
        ["SPACE","DEL","ENTER"]]

# Text
finalText = ""
selectedKey = None
lastClick = time.time()

# Button Class
class Button():
    def __init__(self, pos, text, size=[70,70]):
        self.pos = pos
        self.size = size
        self.text = text

# Create Buttons
buttonList = []

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):

        if key == "SPACE":
            buttonList.append(Button([50,300], key, [280,70]))

        elif key == "DEL":
            buttonList.append(Button([360,300], key, [160,70]))

        elif key == "ENTER":
            buttonList.append(Button([550,300], key, [220,70]))

        else:
            buttonList.append(Button([80*j+50,80*i+50], key))

while True:
    success, img = cap.read()
    img = cv2.flip(img,1)

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    leftIndex = None
    rightPalm = None
    selectedKey = None

    # Detect Hands
    if results.multi_hand_landmarks and results.multi_handedness:

        for handLms, handedness in zip(results.multi_hand_landmarks,
                                       results.multi_handedness):

            label = handedness.classification[0].label

            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h,w,c = img.shape
                cx,cy = int(lm.x*w), int(lm.y*h)
                lmList.append([cx,cy])

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            # LEFT HAND INDEX = SELECT
            if label == "Left":
                leftIndex = lmList[8]

            # RIGHT HAND PALM = ENTER
            if label == "Right":
                rightPalm = lmList[9]   # Center hand point

    # Draw Buttons
    for button in buttonList:
        x,y = button.pos
        w,h = button.size

        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),cv2.FILLED)
        cv2.putText(img,button.text,(x+10,y+45),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

    # LEFT INDEX SELECT KEY
    if leftIndex:
        x1,y1 = leftIndex
        cv2.circle(img,(x1,y1),10,(0,255,0),cv2.FILLED)

        for button in buttonList:
            x,y = button.pos
            w,h = button.size

            if x < x1 < x+w and y < y1 < y+h:
                selectedKey = button.text

                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),cv2.FILLED)
                cv2.putText(img,button.text,(x+10,y+45),
                            cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)

    # RIGHT HAND FULL ENTER
    if rightPalm and selectedKey:

        px,py = rightPalm
        cv2.circle(img,(px,py),12,(0,0,255),cv2.FILLED)

        # If right hand visible = click
        if time.time() - lastClick > 0.8:

            winsound.Beep(1200,120)

            if selectedKey == "SPACE":
                pyautogui.press("space")
                finalText += " "

            elif selectedKey == "DEL":
                pyautogui.press("backspace")
                finalText = finalText[:-1]

            elif selectedKey == "ENTER":
                pyautogui.press("enter")
                finalText += "\n"

            else:
                pyautogui.write(selectedKey)
                finalText += selectedKey

            lastClick = time.time()

    # Text Box
    cv2.rectangle(img,(50,420),(1200,520),(175,0,175),cv2.FILLED)
    cv2.putText(img,finalText[-25:],(60,480),
                cv2.FONT_HERSHEY_SIMPLEX,2,(255,255,255),3)

    cv2.putText(img,"Left Index = Select",(900,35),
                cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2)

    cv2.putText(img,"Right Hand = Enter",(900,70),
                cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2)

    cv2.imshow("Air Typing Keyboard", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()