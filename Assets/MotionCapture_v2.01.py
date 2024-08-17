import cv2
import csv
import pandas as pd
import numpy as np
import socket
import time
import threading
# get 33 landmark (33 x 3 =99 parameter ) using cvzone PoseDetector library
# we will save the landmarks pts in text file & using those text file we will make animation with unity
from cvzone.PoseModule import PoseDetector

flag = [0,0,0]

def receive_data(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            if int(data.decode()) == 1:
                flag[0] = 1
                print(flag[0])
            print("Received:", data.decode())
        except Exception as e:
            print("Error receiving data:", e)
            break

def send_data(sock):
   
    tuple_columns_list = []
    for i in range(0, 33):
        for j in ['x','y','z']:
            tuple_columns_list.append((i,j))

    multi_index_colums = pd.MultiIndex.from_tuples(tuple_columns_list)

     #카메라 연결
    cap1=cv2.VideoCapture(1)
    cap2=cv2.VideoCapture(0)
    detector1 = PoseDetector()
    detector2 = PoseDetector()

    ratio1 = 1
    ratio2 = 1
    posListArr1 = np.empty((0,99))
    posListArr2 = np.empty((0,99))
    temp_array1 = np.empty((0,99))
    temp_array2 = np.empty((0,99))
    temp_array3 = np.empty((0,9))
    cal_array=np.zeros((9))

    while True:
        #Mediapipe 연결
        success1, img1 = cap1.read()
        success2, img2 = cap2.read()
        if not success1 or not success2:
            print("error: camera undetected")
            break
        
        img1 = detector1.findPose(img1)
        img2 = detector2.findPose(img2)
        lmList1, bboxInfo1 = detector1.findPosition(img1)
        lmList2, bboxInfo2 = detector2.findPosition(img2)
        
        if flag[0] == 1:
            #처음 실행시 시간 초기화
            if(flag[0] == 0):
                start_t = time.time()
                flag[0] = 1
            end_t = time.time()
            
            # #1/30초 마다 좌표정보 가져옴
            if(end_t - start_t > 1/30):
                if bboxInfo1:
                    lmString1=''
                    posList1 = []
                    for lm1 in lmList1:
                        posList1.append([lm1[0], img1.shape[0] - lm1[1], lm1[2]])
                    posListArr1 = np.array(posList1)
                    posListArr1 = posListArr1.reshape((99))
                    temp_array1 = np.append(temp_array1, posListArr1.reshape((1,99)), axis = 0)
                
                if bboxInfo2:
                    lmString2=''
                    posList2 = []
                    for lm2 in lmList2:
                        posList2.append([lm2[0], img2.shape[0] - lm2[1], lm2[2]])
                    posListArr2 = np.array(posList2)
                    posListArr2 = posListArr2.reshape((99))
                    temp_array2 = np.append(temp_array2, posListArr2.reshape((1,99)), axis = 0)
                    
                #메인 카메라에 맞춰 길이값 수정
                ratio1 = (posListArr1[14*3+1] - posListArr1[12*3+1])/(posListArr2[14*3+1] - posListArr2[12*3+1])
                ratio2 = (posListArr1[16*3+1] - posListArr1[12*3+1])/(posListArr2[16*3+1] - posListArr2[12*3+1])
                
                cal_array[0] = posListArr1[12*3] - posListArr1[12*3]
                cal_array[1] = posListArr1[12*3+1] - posListArr1[12*3+1]
                cal_array[2] = posListArr2[12*3] - posListArr2[12*3]
                cal_array[3] = posListArr1[14*3] - posListArr1[12*3]
                cal_array[4] = posListArr1[14*3+1] - posListArr1[12*3+1]
                cal_array[5] = ratio1*(posListArr2[14*3] - posListArr2[12*3])
                cal_array[6] = posListArr1[16*3] - posListArr1[12*3]
                cal_array[7] = posListArr1[16*3+1] - posListArr1[12*3+1]
                cal_array[8] = ratio2*(posListArr2[16*3] - posListArr2[12*3])
                temp_array3 = np.append(temp_array3, cal_array.reshape((1,9)), axis = 0)
            
                daqinputvalue1 = cal_array
                data = str(daqinputvalue1).encode()
                length = len(data)
                sock.sendall(length.to_bytes(4, byteorder="big"))   
                sock.sendall(data)
                    
                start_t = end_t

        #웹캠 이미지 출력
        cv2.imshow("output image 1",img1)
        cv2.imshow("output image 2",img2)
        
        # 키보드 입력받고 동작 설정
        key=cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

    #웹캠 해제
    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()

    #save data
    # output_data1 = pd.DataFrame(data=temp_array1, columns=multi_index_colums)
    # output_data2 = pd.DataFrame(data=temp_array2, columns=multi_index_colums)
    # output_data3 = pd.DataFrame(data=temp_array3, columns=['12-x','12-y','12-z','14-x','14-y','14-z','16-x','16-y','16-z'])
    # csv1name = 'data1'
    # csv2name = 'data2'
    # csv3name = 'send_data'
    # csvext = '.csv'
    # csv1path = r'/home/okch/Desktop/project/Motion/Assets/%s%s' % (csv1name,csvext)
    # csv2path = r'/home/okch/Desktop/project/Motion/Assets/%s%s' % (csv2name,csvext)
    # csv3path = r'/home/okch/Desktop/project/Motion/Assets/%s%s' % (csv3name,csvext)
    # output_data1.to_csv(csv1path, index=False)
    # output_data2.to_csv(csv2path, index=False)    
    # output_data3.to_csv(csv3path, index=False)
                

def main():
    HOST = '172.20.10.3'
    PORT = 8053
    
    #Tcp 통신 설정
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # 서버에 연결
            sock.connect((HOST, PORT))

            # 읽기 및 쓰기를 위한 서브 스레드 생성
            receive_thread = threading.Thread(target=receive_data, args=(sock,))
            send_thread = threading.Thread(target=send_data, args=(sock,))

            # 스레드 시작
            receive_thread.start()
            send_thread.start()

            # 메인 스레드는 서브 스레드가 종료되기를 기다림
            receive_thread.join()
            send_thread.join()
    

if __name__ == "__main__":
    main()