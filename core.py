import logging
import socket
import time
import os
import sqlite3
import subprocess
from threading import *

from Logic.Device import Device
from Logic.Player import Players
from Logic.LogicMessageFactory import packets
from Utils.Config import Config

# logging.basicConfig(filename="errors.log", level=logging.INFO, filemode="w")

subprocess.Popen(['python', 'autoshop.py'])

def _(*args):
    print('[INFO]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


def setup_database():
    db_path = './database/Player/plr.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plrs (
            token TEXT, 
            lowID INT, 
            name TEXT, 
            trophies INT, 
            gold INT, 
            gems INT, 
            starpoints INT, 
            tickets INT, 
            Troproad INT, 
            profile_icon INT, 
            name_color INT,
            clubID INT, 
            clubRole INT, 
            brawlerData JSON, 
            brawlerID INT, 
            skinID INT, 
            roomID INT, 
            box INT, 
            bigbox INT, 
            online INT, 
            vip INT, 
            playerExp INT, 
            friends JSON, 
            SCC TEXT,
            trioWINS INT, 
            sdWINS INT, 
            theme INT, 
            quests JSON,
            ban INT
        )
    ''')
    conn.commit()
    conn.close()
    print("[INFO] Database setup completed.")


class Server:
    Clients = {"ClientCounts": 0, "Clients": {}}
    ThreadCount = 0

    def __init__(self, ip: str, port: int):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.port = port
        self.ip = ip

    def start(self):
        if not os.path.exists('./config.json'):
            print("Creating config.json...")
            Config.create_config(self)

        setup_database()

        try:
            self.server.bind((self.ip, self.port))
        except OSError as e:
            print(f"[ERROR] Unable to bind to {self.ip}:{self.port} - {e}")
            return

        _(f'Server started! Ip: {self.ip}, Port: {self.port}')
        while True:
            self.server.listen()
            try:
                client, address = self.server.accept()
                _(f'New connection! Ip: {address[0]}')
                ClientThread(client, address).start()
                Server.ThreadCount += 1
            except Exception as e:
                print(f"[ERROR] Error accepting connection: {e}")


class ClientThread(Thread):
    def __init__(self, client, address):
        super().__init__()
        self.client = client
        self.address = address
        self.device = Device(self.client)
        self.player = Players(self.device)

    def recvall(self, length: int):
        data = b''
        while len(data) < length:
            s = self.client.recv(length - len(data))
            if not s:
                print("Receive Error!")
                break
            data += s
        return data

    def run(self):
        last_packet = time.time()
        try:
            while True:
                header = self.client.recv(7)
                if len(header) > 0:
                    last_packet = time.time()
                    packet_id = int.from_bytes(header[:2], 'big')
                    length = int.from_bytes(header[2:5], 'big')
                    data = self.recvall(length)

                    if packet_id in packets:
                        _(f'Received packet! Id: {packet_id}')
                        message = packets[packet_id](self.client, self.player, data)
                        message.decode()
                        message.process()

                        if packet_id == 10101:
                            Server.Clients["Clients"][str(self.player.low_id)] = {"SocketInfo": self.client}
                            Server.Clients["ClientCounts"] = Server.ThreadCount
                            self.player.ClientDict = Server.Clients

                    else:
                        _(f'Packet not handled! Id: {packet_id}')

                if time.time() - last_packet > 10:
                    print(f"[INFO] Ip: {self.address[0]} disconnected!")
                    self.client.close()
                    break
        except (ConnectionAbortedError, ConnectionResetError, TimeoutError):
            print(f"[INFO] Ip: {self.address[0]} disconnected!")
            self.client.close()


if __name__ == '__main__':
    print("VBC28 REMAKE @lexim0ff")
    server = Server('0.0.0.0', 9339)
    server.start()

