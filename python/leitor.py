import numpy as np
import time 
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pymongo import MongoClient
from datetime import datetime

class GraficoAltura:

    def __init__(self, com:str, port: int):
        client = MongoClient("mongodb://localhost:27017/")
        db = client["meu_banco"]
        self.medicoes = db["medicoes"]
        self.pos0 = 0
        self.acel0 = 0
        self.vel0 = 0
        self.tempo = 0
        self.tempo0 = 0
        self.vel = 0
        self.pos = 0
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

    def calculavel(self):
        self.vel = self.vel0+self.acely*self.tempo

    def calculapos(self):
        
        self.pos = self.pos0+self.vel0*self.tempo+(self.acely*(self.tempo**2)/2)

   

    #script de teste local COMENTAR QUANDO FOR TESTAR DE VERDADE
    def teste(self):
        cont = 0
        acely = 3.2
        flageranegativo = 0
        flagerapositivo = 0
        for i in range(50):
            if acely<= -3.2:
                acely = acely + 1.6
                flagaumenta = 1
                if flageranegativo:
                    flageranegativo = 0
                else:
                    flageranegativo = 1
                msg = f"acelx:2.5, acely:{acely}, acelz:0, gyrx:0, gyry:0,gyrz:0, tempo:{cont}\n"
            elif acely>= 3.2:
                acely = acely - 1.6
                flagaumenta = 0
                if flagerapositivo:
                    flagerapositivo = 0
                else:
                    flagerapositivo = 1
                msg = f"acelx:2.5, acely:{acely}, acelz:0, gyrx:0, gyry:0,gyrz:0, tempo:{cont}\n"
            elif acely == 0:
                if flagerapositivo and not flageranegativo:
                    flagaumenta = 1
                    acely += 1.6
                    msg = f"acelx:2.5, acely:{acely}, acelz:0, gyrx:0, gyry:0,gyrz:0, tempo:{cont}\n"
                elif flageranegativo and not flagerapositivo:
                    flagaumenta = 0
                    acely -=1.6
                    msg = f"acelx:2.5, acely:{acely}, acelz:0, gyrx:0, gyry:0,gyrz:0, tempo:{cont}\n"  
                else:
                    if flagaumenta:
                        acely = acely + 1.6
                        msg = f"acelx:2.5, acely:{acely}, acelz:0, gyrx:0, gyry:0,gyrz:0, tempo:{cont}\n"
                    else:
                        acely = acely - 1.6
                        msg = f"acelx:2.5, acely:{acely}, acelz:0, gyrx:0, gyry:0,gyrz:0, tempo:{cont}\n"
                            
            else:
                if flagaumenta:
                    acely = acely + 1.6
                    msg = f"acelx:2.5, acely:{acely}, acelz:0, gyrx:0, gyry:0,gyrz:0, tempo:{cont}\n"
                else:
                    acely = acely - 1.6
                    msg = f"acelx:2.5, acely:{acely}, acelz:0, gyrx:0, gyry:0,gyrz:0, tempo:{cont}\n"

            self.ser.write(msg.encode('utf-8'))
            print("Enviado:", msg.strip())
            time.sleep(0.5)
            cont+=1

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
                        med = {"Acelz": self.acelz, "Altura": self.altura, "TempoRelativo": self.tempototal, "AlturaPico": self.pico, "TempoReal": temporeal}
                        self.medicoes.insert_one(med)

                        # Empilha novos dados no array numpy
                        self.y_data = np.append(self.y_data, self.altura)
                        self.x_data = np.append(self.x_data, self.tempototal)

                        self.line.set_data(self.x_data, self.y_data)

                        # Ajusta limites do gráfico dinamicamente
                        self.ax.relim()
                        self.ax.autoscale_view()

            except ValueError:
                pass

        return self.line

    def execute(self):
        ani = FuncAnimation(self.fig, self.update, interval=100, cache_frame_data=False)
        plt.show()
        self.ser.close()

