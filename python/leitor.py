import numpy as np
import time 
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pymongo import MongoClient
from datetime import datetime

class GraficoAltura:

    def __init__(self, com:str, port: int, teste: int):
        # client = MongoClient("mongodb://localhost:27017/")
        # db = client["meu_banco"]
        # self.medicoes = db["medicoes"]
        self.pos0 = 0
        self.acel0 = 0
        self.vel0 = 0
        self.tempo = 0
        self.tempo0 = 0
        self.vel = 0
        self.pos = 0
        if teste:
            self.ser = serial.serial_for_url(com,baudrate=port)
        else:
            self.ser = serial.Serial(com,port)
        time.sleep(2)
        #Arrays de dados
        self.x_data = np.array([], dtype=float)
        self.y_data = np.array([], dtype=float)

        # Gráfico 
        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [], 'bo-', markersize=4)
        self.ax.set_xlim(0, 50)
        self.ax.set_ylim(-100, 100)
        self.ax.set_xlabel("Tempo")
        self.ax.set_ylabel("Altura")
   

    #script de teste local COMENTAR QUANDO FOR TESTAR DE VERDADE
    def teste(self):
        for i in range(50):
            msg = f"acelz:2,altura:{i},tempo:{1000*i},pico:{i}\n"

            self.ser.write(msg.encode('utf-8'))
            print("Enviado:", msg.strip())
        return

    #função que atualiza o gráfico
    def update(self,frame):
        #leitura do serial
        if self.ser.in_waiting > 0:
            try:
                line_read = self.ser.readline().decode('utf-8').strip()
                if line_read:
                    # Tratando a linha com formato: acelx:%f, acely:%f
                    partes = line_read.split(',')
                    if len(partes) != 1:
                        print(partes)
                        self.acelz = float(partes[0].split(':')[1])
                        print(f"acelz: {self.acelz}")
                        self.altura = float(partes[1].split(':')[1])
                        print(f"altura: {self.altura}")
                        self.tempototal = float(partes[2].split(':')[1])/1000
                        print(f"tempo: {self.tempototal}")
                        if len(partes) >= 4:
                            self.pico = float(partes[3].split(':')[1])
                        else :
                            self.pico = "não medido"
                        temporeal = datetime.now()
                        

                        # Empilha novos dados no array numpy
                        self.y_data = np.append(self.y_data, self.altura)
                        self.x_data = np.append(self.x_data, self.tempototal)

                        self.line.set_data(self.x_data, self.y_data)

                        # Ajusta limites do gráfico dinamicamente
                        self.ax.relim()
                        self.ax.autoscale_view()
                        try:
                            med = {"Acelz": self.acelz, "Altura": self.altura, "TempoRelativo": self.tempototal, "AlturaPico": self.pico, "TempoReal": temporeal}
                            self.medicoes.insert_one(med)
                        except:
                            print("mongoDb não funcionou") 

            except ValueError:
                print("erro na leitura")
                pass

        return self.line

    def execute(self):
        ani = FuncAnimation(self.fig, self.update, interval=100, cache_frame_data=False)
        plt.show()
        self.ser.close()

