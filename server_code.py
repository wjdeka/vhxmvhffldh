from flask import *
import numpy as np
import mediapipe as mp
from PIL import Image
import cv2
import pytesseract
from pytesseract import Output

# PATH = r'/opt/homebrew/Cellar/tesseract/5.2.0/bin/tesseract'

app = Flask(__name__)



@app.route('/image_upload',methods=['POST'])
def media_pipes() :
    # pytesseract.pytesseract.tesseract_cmd = PATH #테서렉트 패스 지정
    # mp_drawing = mp.solutions.drawing_utils
    # mp_hands = mp.solutions.hands
    # data = request.files['file'].read()

    # jpg_arr = np.frombuffer(data, dtype=np.uint8)
    # img = cv2.imdecode(jpg_arr, cv2.IMREAD_COLOR)
    # d = pytesseract.image_to_data(img, lang='kor', output_type=Output.DICT)
    # print(img.shape)
    
    with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        
        temp = 'recog_False' #클라이언트에게 리턴할 값을 recog_False로 임시 지정
        
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index = hand_landmarks.landmark[8]

                cx = int(index.x*1280)
                cy = int(index.y*720)
                
                cv2.putText(
                    image, text='here', org=(cx,cy),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                    color=255, thickness=2)

                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
        else :
            return 'False'
        try : 
            for i in range(len(d['text'])):
                if d['text'][i] != '':
                    (x,y, x2, y2) =  (d['left'][i], d['top'][i], d['left'][i] + d['width'][i], d['top'][i]+ d['height'][i])
                    cv2.rectangle(image, (x, y), (x2, y2), (0, 255, 0), 2)
                    print((x,y,x2,y2,cx,cy))
                    if x-100<cx and cx <x2+100 and y-100<cy and cy <y2+100:
                        final_result = d['text'][i]
                        a,b,c = final_result
                        
                        
                        temp = f'{a},{b},{c}' #recognition 결과를 temp로 지정
                        
                        
                        print(final_result)
        except :
            pass
    cv2.imwrite('upload.jpg',image) #인식결과에 손가락이 있으면 서버에 인식 결과 사진 저장
    
    print(temp)#인식 결과 출력
    return temp #인식 결과 리턴



app.run(host="0.0.0.0",port=5001) #host는 서버의 IP
