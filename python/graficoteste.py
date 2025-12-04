# grafico.py
import numpy as np
import time
import serial
import matplotlib
matplotlib.use('Agg')  # backend sem janela
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from io import BytesIO

class GraficoAltura:

    def __init__(self, port:str):
        self.pos0 = 0
        self.acel0 = 0
        self.vel0 = 0
        self.tempo = 0
        self.tempo0 = 0
        self.vel = 0
        self.pos = 0

        self.ser = serial.serial_for_url(port, 9600, timeout=1)
        time.sleep(2)

        self.x_data = np.array([], dtype=float)
        self.y_data = np.array([], dtype=float)

        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [], 'bo-', markersize=4)
        self.ax.set_xlim(0, 50)
        self.ax.set_ylim(-100, 100)
        self.ax.set_xlabel("Tempo")
        self.ax.set_ylabel("Altura")

        # inicia animação
        self.ani = FuncAnimation(self.fig, self.update, interval=100)

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

    def calculavel(self):
        self.vel = self.vel0 + self.acely * self.tempo

    def calculapos(self):
        self.pos = self.pos0 + self.vel0 * self.tempo + (self.acely * (self.tempo**2) / 2)

    def update(self, frame):
        if self.ser.in_waiting > 0:
            try:
                line_read = self.ser.readline().decode('utf-8').strip()
                if line_read:
                    partes = line_read.split(',')
                    self.acelx = float(partes[0].split(':')[1])
                    self.acely = float(partes[1].split(':')[1])
                    self.acelz = float(partes[2].split(':')[1])
                    self.gyrx = float(partes[3].split(':')[1])
                    self.gyry = float(partes[4].split(':')[1])
                    self.gyrz = float(partes[5].split(':')[1])
                    self.tempototal = float(partes[6].split(':')[1])

                    self.tempo = self.tempototal - self.tempo0
                    self.tempo0 = self.tempototal

                    self.calculavel()
                    self.calculapos()

                    self.vel0 = self.vel
                    self.pos0 = self.pos

                    self.y_data = np.append(self.y_data, self.pos)
                    self.x_data = np.append(self.x_data, self.tempototal)

                    self.line.set_data(self.x_data, self.y_data)

                    self.ax.relim()
                    self.ax.autoscale_view()

            except ValueError:
                pass

        return self.line

    # MÉTODO IMPORTANTE: renderiza o frame PNG
    def get_frame(self):
        buf = BytesIO()
        self.fig.savefig(buf, format="png")
        buf.seek(0)
        return buf.read()

    # STREAMING: gera frames infinitamente
    def stream(self):
        while True:
            frame = self.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')
