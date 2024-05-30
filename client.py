import socket
import threading
import time
import sys

class TCPClient:

    my_info = {}

    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.TOKEN_MAX_BYTE = 255
        self.ROOM_NAME_MAX_BYTE = 2 ** 8 # 入力の部分で関数を作る
        self.PAYLOAD_MAX_BYTE = 2 ** 29 # 入力の部分で関数を作る
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # ヘッダーの作成
    def protocol_header(self, room_name, operation, state, payload):
        room_name_size = len(room_name)
        payload_size = len(payload)
        return room_name_size.to_bytes(1, "big") + operation.to_bytes(1, "big") + state.to_bytes(1,"big") + payload_size.to_bytes(29, "big")
    
    # ユーザー名の入力
    def input_username(self):
        username = input("ユーザー名を入力してください -> ")

        if len(username) > self.PAYLOAD_MAX_BYTE:
            print("2^29バイトを超えています. 再度入力してください.")
            return self.input_username()
        elif len(username) == 0:
            return self.input_username()
        else:
            return username
        
    # ルーム名の入力
    def input_roomname(self, operation):

        if (operation == 1):
            room_name = input("作成するルーム名を入力してください -> ")
            if len(room_name) > self.ROOM_NAME_MAX_BYTE:
                print("2^8バイトを超えています. 再度入力してください.")
                return self.input_roomname()
            elif len(room_name) == 0:
                return self.input_roomname()
            else:
                return room_name
        
        else:
            room_name = input("参加したいルーム名を入力してください -> ")
            if len(room_name) > self.ROOM_NAME_MAX_BYTE:
                print("2^8バイトを超えています. 再度入力してください.")
                return self.input_roomname()
            elif len(room_name) == 0:
                return self.input_roomname()
            else:
                return room_name
    

    def tcp_main(self):
        # サーバーが待ち受けているポートにソケットします．
        print("connecting to {}".format(self.server_address, self.server_port))

        try:
            # 接続後，サーバーとクライアントが相互に読み書きできるようになります．
            self.sock.connect((self.server_address, self.server_port))
        except socket.error as err:
            print("Error connectiong to server: ", err)
            return
        
        print("接続できました.")
        TCPClient.my_address = self.sock.getsockname()

        try:
            user_name = self.input_username()

            operation = int(input("1または2を入力してください (1: ルーム作成, 2: ルームに参加) -> "))

            if (operation == 1):
                room_name = self.input_roomname(operation)
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
                self.sock.send(data) # ヘッダー + ボディ を送信
                my_token = self.sock.recv(self.TOKEN_MAX_BYTE)
            else:
                self.sock.send(data) # ヘッダー + ボディ を送信
                room_name_list = self.sock.recv(4096)
                print(room_name_list)
                room_name = self.input_roomname(operation)
                room_name_bytes = room_name.encode("utf-8")
                self.sock.send(room_name_bytes)
                my_token = self.sock.recv(self.TOKEN_MAX_BYTE)
                
            print("tokenを受け取りました -> ", my_token)
            self.my_info = {my_token : [room_name, user_name]} 
            print(self.my_info)

        except socket.error as err:
            print("Socket error: ", err)
        except Exception as e:
            print("Error: ", e)

        finally:
            print("closing socket")
            self.sock.close()
    
    def start(self):
        self.tcp_main()
        return self.my_info

class UDPClient:
    def __init__(self, server_address, server_port, my_info):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.my_info = my_info
        self.room_name = ''
        self.username = ''
    
    # サーバに接続後,最初にusernameを入力
    def send_username(self):
            USER_NAME_MAX_BYTE_SIZE = 255

            # 以下の処理は関数にする予定
            for token in self.my_info:
                my_token = token

            self.room_name = self.my_info[my_token][0]
            print(self.room_name)

            roomname_size = len(self.room_name).to_bytes(1, "big")
            token_size = len(my_token).to_bytes(1, "big")

            header = roomname_size + token_size
            data = header + self.room_name.encode("utf-8") + my_token

            # 問題がなければサーバに送信
            self.sock.sendto(data, (self.server_address, self.server_port))
            

    # username入力後の処理
    def send_message(self):
        while True:
            message = input("")
            print("\033[1A\033[1A") # "\033[1A": カーソルを現在の行の先頭に移動 -> これにより、ターミナル上の出力を更新または消去
            
            # 以下の処理は処理は関数にしたい
            for token in self.my_info:
                my_token = token
            
            self.room_name = self.my_info[my_token][0]
            roomname_size = len(self.room_name).to_bytes(1, "big")
            token_size = len(my_token).to_bytes(1, "big")

            header = roomname_size + token_size
            data = header + self.room_name.encode("utf-8") + my_token + message.encode()

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

            elif (rcv_data == "exit!"): # ルームホストが退出した場合
                print(rcv_data)
                self.sock.close()
                sys.exit()
                
            else:
                print(rcv_data)


    def start(self):
        self.send_username()
        
        print("self.sock.getsockname(): ", self.sock.getsockname())
        print("TCPClient.my_address: ", TCPClient.my_address)
        
        # 並列処理
        thread_send = threading.Thread(target = self.send_message)
        thread_receive = threading.Thread(target = self.receive_message)

        thread_send.start()
        thread_receive.start()
        thread_send.join()
        thread_receive.join()


if __name__ == "__main__":

    server_address = '0.0.0.0'
    tcp_server_port = 9001
    udp_server_port = 9002

    tcp_client = TCPClient(server_address, tcp_server_port)
    my_info = tcp_client.start()

    udp_client = UDPClient(server_address, udp_server_port, my_info)
    udp_client.start()