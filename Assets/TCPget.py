import pandas as pd
import numpy as np
import socket
import threading

def receive_data(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print("Received:", data.decode())
        except Exception as e:
            print("Error receiving data:", e)
            break

def send_data(sock):
    while True:
        try:
            message = input("Enter message to send: ")
            sock.sendall(message.encode())
        except Exception as e:
            print("Error sending data:", e)
            break

def main():
    HOST = '172.30.1.87'  # 서버 주소
    PORT = 8053       # 포트 번호

    # 소켓 생성
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
