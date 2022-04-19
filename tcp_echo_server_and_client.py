# Client and server for tcp echo.
import sys
from socket import *
from _thread import *

# ECHO_PORT 기본 포트
ECHO_PORT = 9190

# 버퍼 사이즈
BUFSIZE = 1024

# 서버 대기 큐
QUEUE_LIMIT = 5

isRunning = False


# 메인 함수
def main():
    # 매개변수가 2개보다 적다면
    if len(sys.argv) < 2:
        # 사용 방법 표시
        usage()

    # 첫 매개변수가 '-s' 라면
    if sys.argv[1] == '-s':
        # 서버 함수 호출
        server()

    # 첫 매개변수가 '-c' 라면
    elif sys.argv[1] == '-c':
        # 클라이언트 함수 호출
        client()

    # '-s' 또는 '-c' 가 아니라면
    else:
        # 사용 방법 표시
        usage()


# 사용하는 방법 화면에 표시하는 함수
def usage():
    sys.stdout = sys.stderr
    print('Usage: python tcpecho.py -s [port]            (server)')
    print('or:    python tcpecho.py -c host [port] <file (client)')
    # 종료
    sys.exit(2)


# 서버 함수
def server():
    # 매개 변수가 2개 초과라면
    # ex>$ python tcp_echo_server_and_client.py -s 8001
    if len(sys.argv) > 2:
        # 두번째 매개변수를 포트로 지정
        port = eval(sys.argv[2])

    # 매개 변수가 2개 라면
    # ex>$ python tcpecho.py -s
    else:
        # 기본 포트로 설정
        port = ECHO_PORT

    # 소켓 생성 (UDP = SOCK_DGRAM, TCP = SOCK_STREAM)
    s = socket(AF_INET, SOCK_STREAM)

    # 포트 설정
    s.bind(('', port))

    # 포트 ON
    s.listen(QUEUE_LIMIT)

    # 준비 완료 화면에 표시
    print('tcp echo server ready')

    # 연결 대기
    print('wait for client... ')
    c_sock, addr = s.accept()

    print('connected to {}:{}'.format(addr[0], addr[1]))

    isRunning = True
    # 루프 돌면서 클라이언트로 들어온 데이터 그대로 재 전송
    while (isRunning):
        readBuf = c_sock.recv(BUFSIZE)
        if len(readBuf) == 0:
            break
        print('read data {}, length {}'.format(readBuf.decode('utf-8'), len(readBuf)))
        c_sock.send(readBuf)
    print('disconnected ')
    c_sock.close()
    s.close()


# 클라이언트 함수
def client():
    # 매개변수가 3개 미만 이라면
    if len(sys.argv) < 3:
        # 사용 방법 화면에 출력
        # usage함수에서 프로그램 종료
        usage()

    # 두번째 매개변수를 서버 IP로 설정
    host = sys.argv[2]

    # 매개변수가 3개를 초과하였다면(4개라면)
    # ex>$ python tcp_echo_server_and_client.py -c 127.0.0.1 8001
    if len(sys.argv) > 3:
        # 3번째 매개변수를 포트로 설정
        port = eval(sys.argv[3])

    # 초과하지 않았다면(즉, 3개라면)
    # ex>$ python tcp_echo_server_and_client.py -c 127.0.0.1
    else:
        # 기본 포트로 설정
        port = ECHO_PORT

    # IP 주소 변수에 서버 주소와 포트 설정
    addr = host, port

    # 소켓 생성
    s = socket(AF_INET, SOCK_STREAM)

    try:
        s.connect(addr)
    except Exception as e:
        print('connection failed')
        sys.exit(2)

    # 연결되어 준비 완료 화면에 출력
    print('connected! \n tcp echo client ready')

    # 무한 루프
    isRunning = True
    while isRunning:
        # 터미널 창(입력창)에서 타이핑을하고 ENTER키를 누를때 까지
        txt = sys.stdin.readline()

        # 변수에 값이 없다면
        if not txt:
            break

        # 개행 제거
        txt = txt.replace('\n', '')

        # 입력받은 텍스트를 서버로 발송
        sent = s.send(txt.encode())
        if sent == 0:
            print("socket connection broken")
            break

        # 리턴 대기
        # 수신되는 데이터를 저장할 리스트 변수
        chunks = []

        # 수신된 데이터 총 길이를 저장하는 변수
        bytes_cnt = 0

        # sent는 송신한(전송한) 데이터의 길이
        # 수신되는 데이터가 송신한 데이터보다 클때까지 while 루프
        while bytes_cnt < sent:

            # 수신 데기 - 이때 블럭 상태이므로 데이터가 수신되기 전까진
            # 아래의 루틴을 진행하지 않고 대기하고 있음
            chunk = s.recv(BUFSIZE)

            # 수신된 데이터가 비어있다면
            if chunk == b'':
                # 연결이 끊어졌다고 판단하여 수신 루프에서 빠져나가고 종료함.
                isRunning = False
                print("read error")
                break

            # 수신된 데이터 chunk를 chunks 리스트에 추가함
            chunks.append(chunk)

            # 수신된 데이터 chunk의 길이를 bytes_cnt에 넣어 수신된 총 길이를 증가시킴
            bytes_cnt = bytes_cnt + len(chunk)
            # 다시 while 루프의 처음으로 이동

        # 지금까지 수신된 데이터 리스트 chunks를 문자열 하나로 합친다.
        # ex> chunks가 ['he', 'll', 'o']라면
        # data = b'hello'로 변경
        data = b''.join(chunks)

        # 서버로부터 받은 메시지 출력
        print('client received {}'.format(data))

    s.close()
    print('close')


main()