import socket
import threading
import time
import secrets

class TCPServer:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.HEADER_MAX_BYTE = 32
        self.TOKEN_MAX_BYTE = 255
        self.client_map = {} # {client_address : [token, payload(username), host(0:guest, 1:host), room_name]}
        self.room_member_map = {} # {room_name : [token, client_address]}
        

    def tcp_main(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.server_address, self.server_port)) # server_address: 0.0.0.0 server_port: 9002
        sock.listen(1)
        print("server listening...")
        

        while True:
            connection, client_address = sock.accept()
            try:
                print("connection from", client_address)
                '''
                while True:
                    data = connection.recv(4096)  # 1024バイトごとにデータを受け取る（適宜サイズを調整）
                    if not data:
                        break  # データを受け取らなくなったらループを抜ける
                '''
                data = connection.recv(4096) # ヘッダー+ボディ の受け取り

                header = data[:self.HEADER_MAX_BYTE]
                #print("header: ", header)
                
                room_name_size = int.from_bytes(header[:1], "big")
                operation = int.from_bytes(header[1:2], "big")
                state = int.from_bytes(header[2:3], "big")
                payload_size = int.from_bytes(header[3:self.HEADER_MAX_BYTE], "big")


                print("------------------------------")
                print("room_name_size: ", room_name_size)
                print("operation: ", operation)
                print("state: ", state)
                print("payload_size: ", payload_size)

                print("------------------------------")
                print("Recive header from client.")
                print("Byte length: RoomNameSize: {}, Operation: {}, State: {}, PayloadSize: {}".format(room_name_size, operation, state, payload_size))
                print("------------------------------")

                body = data[self.HEADER_MAX_BYTE:]
                room_name = body[:room_name_size].decode("utf-8")
                payload = body[room_name_size:room_name_size + payload_size].decode("utf-8") # username

                # print("body: ", body)
                print("room_name: ", room_name)
                print("payload: ", payload)
                
                #print(self.client_token)

                token = secrets.token_bytes(self.TOKEN_MAX_BYTE)

                if (operation == 1):
                    host = 1
                    connection.send(token)
                    self.room_member_map[room_name] = [[token, client_address]]
                    print("新しいルームを作成します (Host: {})".format(payload))

                elif (operation == 2):
                    host = 0
                    connection.send(str(self.room_member_map.keys()).encode("utf-8"))
                    room_name = connection.recv(4096).decode("utf-8")
                    print("room_nameを受け取りました -> ", room_name)
                    self.room_member_map[room_name].append([token, client_address])
                    connection.send(token)
                    print(self.room_member_map)
                    print("既存のルームに参加します")

                self.client_map.update({client_address : [token, payload, host, room_name]})

            except Exception as e:
                print('Error: ' + str(e))
            
            finally:
                connection.close()
            

'''

class UDPServer:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        # self.clients = []
        self.clientsmap = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.server_address, self.server_port))
        print("サーバが起動しました")
        print('waiting to receive message')
        print("--------------------------")
    
    # クライアントからのメッセージ受信処理 及び 他ユーザへの送信
    def handle_message(self):
        while True:

            data, client_address = self.sock.recvfrom(4096) # 最大4096byteのデータを受信
            # 新しいクライアントからの受信 -> clientsリストにアドレスを保存
            if (not client_address in self.clientsmap):
                name = data.decode('utf-8')
                # print("新しいユーザーです -> ", name)
                # self.clients.append(client_address)
                self.clientsmap.update({client_address : [name, time.time()]})
                #print(client_address)
                #print("新しいユーザーです -> ", self.clientsmap[client_address], time.ctime())
                print("新しいユーザーです -> ", name)

            else:
                self.clientsmap[client_address][1] = time.time() # クライアントの最終送信時刻を更新
                usernamelen = data[0] # 最初のバイトがユーザー名の長さを表す
                username = data[1:usernamelen + 1].decode() # ユーザー名を取得
                message = data[usernamelen + 1:].decode() # メッセージを取得
                print(f"{username}: {message}")
                self.relay_message(username + ": " + message) # 接続ユーザ全員に送信(送信元のユーザも含む)
    
    # リレーシステム
    def relay_message(self, message):
        for client_address in self.clientsmap.keys():
            self.sock.sendto(message.encode(), client_address)
    
    # 各クライアントの最後の最後のメッセージ送信時刻を追跡
    def send_time_tracking(self):
        while True:
            time.sleep(60)# 1分単位で追跡
            print("スリープ解除")
            try:
                for address, value in self.clientsmap.items():
                    send_time = value[1]
                    if (time.time() - send_time > 300): # クライアントからの通信が5分なければclientsmapから情報を削除
                        self.clientsmap.pop(address)
                        self.sock.sendto("Timeout!".encode(), address)
                        print(value[0], address, "connection has been lost.")
            except Exception as e: # ハッシュマップの中身がない時のエラー処理
                pass

    def start(self):
        thread_main = threading.Thread(target = self.handle_message)
        thread_tracking = threading.Thread(target = self.dsend_time_tracking)
        thread_main.start()
        thread_tracking.start()
        thread_main.join()
        thread_tracking.join()
'''
if __name__ == "__main__":
    server_address = '0.0.0.0'
    server_port = 9001
    print('starting up on port {}'.format(server_port))
    server = TCPServer(server_address, server_port)
    server.tcp_main()

    #server = UDPServer(server_address, server_port)
    #server.start()