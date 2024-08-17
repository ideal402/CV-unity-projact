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
    cal_array=np.zeros((9))

    while True:

        
        if flag[0] == 1:
            #처음 실행시 시간 초기화
            if(flag[0] == 0):
                start_t = time.time()
                flag[0] = 1
            end_t = time.time()
            
            # #1/30초 마다 좌표정보 가져옴
            if(end_t - start_t > 1/30):
           
            
                daqinputvalue1 = cal_array
                data = str(daqinputvalue1).encode()
                length = len(data)
                sock.sendall(length.to_bytes(4, byteorder="big"))   
                sock.sendall(data)
                    
                start_t = end_t


def main():
    HOST = '172.20.10.8'
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