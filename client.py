import socket
import threading
import time
import sys

class TCPClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.TOKEN_MAX_BYTE = 255

    def protocol_header(self, room_name, operation, state, payload):
        room_name_size = len(room_name)
        payload_size = len(payload)
        return room_name_size.to_bytes(1, "big") + operation.to_bytes(1, "big") + state.to_bytes(1,"big") + payload_size.to_bytes(29, "big")
    
    def tcp_main(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # サーバーが待ち受けているポートにソケットします．
        print("connecting to {}".format(self.server_address, self.server_port))

        try:
            # 接続後，サーバーとクライアントが相互に読み書きできるようになります．
            sock.connect((self.server_address, self.server_port))
        except socket.error as err:
            print("Error connectiong to server: ", err)
            return
            #print(err)
            #sys.exit(1)

        print("接続できました")

        try:
            user_name = input("ユーザー名を入力してください -> ")

            operation = int(input("1または2を入力してください (1: ルーム作成, 2: ルームに参加) -> "))

            if (operation == 1):
                room_name = input("ルーム名を入力してください -> ")
            else:
                room_name = " "
                
            state = 0
            payload = user_name

            header = self.protocol_header(room_name, operation, state, payload)
            room_name_bytes = room_name.encode("utf-8")
            payload_bytes = payload.encode("utf-8")

            data = header + room_name_bytes + payload_bytes

            '''
            print(----------------)
            print("header: ", header)
            print("\n")
            print("data: ", data)
            print(----------------)
            '''

            if (operation == 1):
                sock.send(data) # ヘッダー + ボディ を送信
                token = sock.recv(self.TOKEN_MAX_BYTE)
            else:
                sock.send(data) # ヘッダー + ボディ を送信
                room_name_list = sock.recv(4096)
                print(room_name_list)
                room_name = input("参加したいルーム名を入力してください -> ")
                room_name_bytes = room_name.encode("utf-8")
                sock.send(room_name_bytes)
                token = sock.recv(self.TOKEN_MAX_BYTE)
                


            print("tokenを受け取りました -> ", token)

        except socket.error as err:
            print("Socket error: ", err)
        except Exception as e:
            print("Error: ", e)

        finally:
            print("closing socket")
            sock.close()
        
'''
class UDPClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_address = ''
        self.client_port = self.find_free_port()
        self.client_info = str(self.client_address)+ "," + str(self.client_port)
        self.sock.bind((self.client_address, self.client_port))
        self.username = ''
    
    # サーバに接続後,最初にusernameを入力
    def input_username(self):
            USER_NAME_MAX_BYTE_SIZE = 255
            self.username = input("Please enter your username: ") # username入力
            # 何も入力がなければやり直し
            if self.username == '':
                print("Input is incorrect!")
                self.input_username()

            username_size = len(self.username.encode("utf-8"))

            # バイトサイズが255バイトより大きければやり直し
            if username_size > USER_NAME_MAX_BYTE_SIZE:
                print("User name byte: " + str(username_size) + " is too large.")
                print("The user name must not exceed 255 bytes.")
                self.input_username()
            
            # 問題がなければサーバに送信
            self.sock.sendto(self.username.encode('utf-8'), (self.server_address, self.server_port))
    
    # username入力後の処理
    def send_message(self):
        while True:
            message = input("")
            print("\033[1A\033[1A") # "\033[1A": カーソルを現在の行の先頭に移動 -> これにより、ターミナル上の出力を更新または消去
            #print("You: " + message)
            usernamelen = len(self.username).to_bytes(1, byteorder='big')# UTF-8 エンコーディングを使用して変換 (指定されたバイト数（ここでは1バイト）のバイト列に変換します)
            data = usernamelen + self.username.encode() + message.encode() # ユーザー名とメッセージを結合して送信
            # サーバへのデータ送信
            self.sock.sendto(data, (self.server_address, self.server_port))
            time.sleep(0.1)

    # 他ユーザのメッセージの受信処理
    def receive_message(self):
        while True:
            rcv_data = self.sock.recvfrom(4096)[0].decode("utf-8")

            if (rcv_data == "Timeout!"): # タイムアウト処理
                print(rcv_data)
                self.sock.close()
                sys.exit()
            else:
                print(rcv_data)


    # 空きポートの割り当て
    def find_free_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', 0)) # ソケットにローカルホスト上の空きポートをバインド (ポート番号を0に指定でOS空きポートを自動的に割り当て)
        port = sock.getsockname()[1] # ソケットがバインドされているアドレス情報を取得(port番号)
        sock.close()
        return port

    def start(self):
        self.input_username()
        # 並列処理
        thread_send = threading.Thread(target = self.send_message)
        thread_receive = threading.Thread(target = self.receive_message)

        thread_send.start()
        thread_receive.start()
        thread_send.join()
        thread_receive.join()
'''

if __name__ == "__main__":

    server_address = '0.0.0.0'
    server_port = 9001

    client = TCPClient(server_address, server_port)
    client.tcp_main()

    #client = UDPClient(server_address, server_port)
    #client.start()