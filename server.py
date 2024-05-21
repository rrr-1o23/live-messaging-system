import socket
import threading
import time
import secrets



class TCPServer:

    room_members_map = {} # {room_name : [token, token, token, ...]}
    clients_map = {} # {token : [client_address, room_name, payload(username), host(0:guest, 1:host)]}

    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.server_address, self.server_port)) # server_address: 0.0.0.0 server_port: 9002
        self.HEADER_MAX_BYTE = 32
        self.TOKEN_MAX_BYTE = 255
        

    def tcp_main(self):
        
        while True:

            try:
                self.sock.listen()
                print("server listening...")
                connection, client_address = self.sock.accept()
                print("connection from", client_address)
                
                data = connection.recv(4096) # ヘッダー+ボディ の受け取り
                header = data[:self.HEADER_MAX_BYTE]
                
                room_name_size = int.from_bytes(header[:1], "big")
                operation = int.from_bytes(header[1:2], "big")
                state = int.from_bytes(header[2:3], "big")
                payload_size = int.from_bytes(header[3:self.HEADER_MAX_BYTE], "big")

                '''
                print("------------------------------")
                print("room_name_size: ", room_name_size)
                print("operation: ", operation)
                print("state: ", state)
                print("payload_size: ", payload_size)

                print("------------------------------")
                print("Recive header from client.")
                print("Byte length: RoomNameSize: {}, Operation: {}, State: {}, PayloadSize: {}".format(room_name_size, operation, state, payload_size))
                print("------------------------------")
                '''

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
                    self.room_members_map[room_name] = [token]
                    #print(self.room_member_map)
                    print("新しいルームを作成します (Host: {})".format(payload))

                elif (operation == 2):
                    host = 0
                    connection.send(str(self.room_members_map.keys()).encode("utf-8"))
                    room_name = connection.recv(4096).decode("utf-8")
                    print("クライアントが参加したいルーム名を受け取りました -> ", room_name)
                    self.room_members_map[room_name].append(token)
                    connection.send(token)
                    #print(self.room_member_map)
                    print("既存のルームに参加します")

                
            except Exception as e:
                print('Error: ' + str(e))
            
            finally:
                self.clients_map[token] = [client_address, room_name, payload, host, None]
                print(self.clients_map)
                connection.close()

    def start(self):
        self.tcp_main()
        #thread_main = threading.Thread(target = self.tcp_main)
        #thread_main.start()
        #thread_main.join()





class UDPServer:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.room_members_map = TCPServer.room_members_map # TCP通信から引き継ぎ {room_name : {token : address}, ...}
        self.clients_map = TCPServer.clients_map # {token : [client_address, room_name, payload(username), host]}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.server_address, self.server_port))
        print("サーバが起動しました")
        print('waiting to receive message')
        print("--------------------------")
    
    # クライアントからのメッセージ受信処理 及び 他ユーザへの送信
    def handle_message(self):
        while True:
            
            data, client_address = self.sock.recvfrom(4096) # 最大4096byteのデータを受信
            #print("connection from ", client_address)

            header = data[:2]
            room_name_size = int.from_bytes(header[:1], "big")
            token_size = int.from_bytes(header[1:2], "big")
            #print(roomname_size, token_size)

            body = data[2:]
            room_name = body[:room_name_size].decode("utf-8")
            token = body[room_name_size:room_name_size + token_size]
            #print("roomname:",roomname)
            #print("token:\n", token)
            #print(self.room_members_map)
            #print('TCPSever: ', TCPServer.clients_map)


            # TCPのアドレスに上書き
            if self.clients_map[token][0] != client_address:
                self.clients_map[token][0] = client_address # [client_address, room_name, payload, host, None]
                print("ルーム{}に{}が参加しました.".format(self.clients_map[token][1], self.clients_map[token][2]))
        
            else:
                self.clients_map[token][-1] = time.time() # クライアントの最終送信時刻を更新
                username = self.clients_map[token][2]
                message = username + ": " + body[room_name_size + token_size:].decode("utf-8")
                print("Room: {}, User: {}".format(room_name, username))
                print(message,"\n")
                self.relay_message(room_name, message) # 接続ユーザ全員に送信(送信元のユーザも含む)

            '''
            # 新しいクライアントからの受信 -> clientsリストにアドレスを保存
            if (not client_address in self.clientsmap):
                self.tcp_server_roommember[roomname][token] = client_address
                print(self.tcp_server_roommember)
                #data = data.decode('utf-8')
                #print("新しいユーザーです -> ", name)
                #self.clients.append(client_address)
                #self.clientsmap.update({client_address : [username, time.time()]})
                #print(client_address)
                #print("新しいユーザーです -> ", self.clientsmap[client_address], time.ctime())
                #print("新しいユーザーです -> ", data)
                #tcp_server_roommem = TCPServer.room_member_map
                #print(self.tcp_server_roommember)
            '''
    
    # リレーシステム
    def relay_message(self, room_name, message):
        members = self.room_members_map[room_name]

        for member_token in members:
            member_address = self.clients_map[member_token][0]
            self.sock.sendto(message.encode(), member_address)
    

    # 各クライアントの最後の最後のメッセージ送信時刻を追跡
    def send_time_tracking(self):
        while True:
            time.sleep(60)# 1分単位で追跡
            print("スリープ解除")
            try:
                for client_token, client_info_list in self.clients_map.items():
                    last_send_time = client_info_list[-1] # クライアントの最終送信時刻

                    if (time.time() - last_send_time > 300): # クライアントからの通信が5分なければclientsmapから情報を削除
                        belonging_room = client_info_list[1] # 該当tokenが所属しているルーム
                        deleted_user = client_info_list[2] # 該当トークンユーザー
                        

                        # 削除されるクライアントがルームホストの場合の処理をここに入れたい
                        if (self.clients_map[client_token][3] == 1): # 削除されるユーザーがhostの場合
                            notice = "ホストの{}がルームを退出しました．".format(deleted_user)
                            self.relay_message(belonging_room, notice)
                            self.relay_message(belonging_room, "exit!")
                            del self.room_members_map[belonging_room] # ホストのルームを消去

                        else:
                            self.sock.sendto("Timeout!".encode(), client_info_list[0])
                            self.room_members_map[belonging_room].remove(client_token) # ルームメンバーから削除
                            del self.clients_map[client_token] # クライアントリストから削除

            except Exception as e: # ハッシュマップの中身がない時のエラー処理
                pass
    

    def start(self):
        thread_main = threading.Thread(target = self.handle_message)
        thread_tracking = threading.Thread(target = self.send_time_tracking)
        thread_main.start()
        thread_tracking.start()
        thread_main.join()
        thread_tracking.join()
    
if __name__ == "__main__":
    server_address = '0.0.0.0'
    tcp_server_port = 9001
    udp_server_port = 9002

    tcp_server = TCPServer(server_address, tcp_server_port)
    udp_server = UDPServer(server_address, udp_server_port)

    thread_tcp = threading.Thread(target = tcp_server.start)
    thread_udp = threading.Thread(target = udp_server.start)

    thread_tcp.start()
    thread_udp.start()

    thread_tcp.join()
    thread_udp.join()



    '''
    tcp_server = TCPServer(server_address, tcp_server_port)
    udp_server = UDPServer(server_address, udp_server_port)
    tcp_server.start()
    udp_server.start()
    '''