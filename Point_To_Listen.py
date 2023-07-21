import threading, cv2, time, uuid, requests, json, playsound
import mediapipe as mp
from gtts import gTTS

def speak(text):
    tts=gTTS(text=text, lang='ko')
    filename='voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)

def Naver_OCR(api_url, secret_key):
    while True:
        global img_path
        if img_path == None:
            continue
        path = img_path
        files = [('file', open(path,'rb'))]


        request_json = {'images': [{'format': 'jpg',
                                        'name': 'demo'
                                    }],
                            'requestId': str(uuid.uuid4()),
                            'version': 'V2',
                            'timestamp': int(round(time.time() * 1000))
                        }
                            
        payload = {'message': json.dumps(request_json).encode('UTF-8')}
                            
        headers = {
        'X-OCR-SECRET': secret_key,
        }
                            
        response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
        result = response.json()

        #print(result)

        text_center_dict = {}
        try:
            for field in result['images'][0]['fields']:
                if field['inferConfidence'] < 0.95:
                    continue
                text = field['inferText']
                vertices_list = field['boundingPoly']['vertices']
                pts = [tuple(vertice.values()) for vertice in vertices_list]
                topLeft = [int(_) for _ in pts[0]]
                bottomRight = [int(_) for _ in pts[2]]
                OCR_cx = (topLeft[0] + bottomRight[0]) / 2.0
                OCR_cy = (topLeft[1] + bottomRight[1]) / 2.0
                text_center_dict[text] = (OCR_cx, OCR_cy)
            global text_candidate_dict
            text_candidate_dict = text_center_dict
        except:
            continue

if __name__ == "__main__":
    api_url = 'https://j0zhn9mbq0.apigw.ntruss.com/custom/v1/17560/c23bcf9c873aec90ecb7718f5bab8f33446390da6e0dee26d88cd4218370fe49/general'
    secret_key = 'U1FZaldUR2hwa1pPa0pqVmdtaU51dkdsb2djdkdOTnc='

    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

        img_path = None
        text_candidate_dict = {}
        naver_ocr = threading.Thread(target=Naver_OCR, args=(api_url, secret_key), daemon=True)
        naver_ocr.start()

        nearest_text = None

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                continue

            cv2.imwrite('cap.jpg',image)
            img_path = 'cap.jpg'
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    index = hand_landmarks.landmark[8]
                    finger_cx = int(index.x*1280)
                    finger_cy = int(index.y*720)
                    #print(finger_cx,finger_cy)

                    cv2.putText(
                        image, text='here', org=(finger_cx,finger_cy),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                        color=255, thickness=2)

                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    prior_text = nearest_text

                    if text_candidate_dict == {}:
                        continue

                    #distance_dict = {}
                    distance_list = []

                    for text in text_candidate_dict.keys():
                        center = text_candidate_dict[text]
                        distance = ((center[0] - finger_cx)**2.0 + (center[1] - finger_cy)**2.0)**(1/2)
                        #distance_dict[text] = distance
                        distance_list.append(distance)
                        if min(distance_list) == distance:
                            if distance <= 55:
                                nearest_text = text
                    
                    #print(distance_dict)

                    if nearest_text == prior_text:
                        continue

                    print(nearest_text)
                    speak(nearest_text)
            cv2.imshow('cap.jpg', image)
            if cv2.waitKey(1) == ord('q'):
                break
        cap.release()
