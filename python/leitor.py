import numpy as np
import time 
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

global pos0
global pos
global acel
global vel0
global vel
global tempo
global tempo0
pos0 = 0
acel0 = 0
vel0 = 0
tempo = 0
tempo0 = 0

def calculavel():
    global vel, vel0, acel, tempo
    vel = vel0+acel*tempo

def calculapos():
    global pos0, pos, acel, acel0, vel0, vel, tempo
    pos = pos0+vel0*tempo+(acel*(tempo**2)/2)

# def calculapos():


# Cria a Serial (trocar serial_for_url por Serial quando testar com o arduino)
ser = serial.serial_for_url('loop://',9600, timeout=1)

#espera a conexão
time.sleep(2)

#Arrays de dados
x_data = np.array([], dtype=float)
y_data = np.array([], dtype=float)

# Gráfico 
fig, ax = plt.subplots()
(line,) = ax.plot([], [], 'bo-', markersize=4)
ax.set_xlim(0, 50)
ax.set_ylim(-100, 100)
ax.set_xlabel("Tempo")
ax.set_ylabel("Altura")

#script de teste local COMENTAR QUANDO FOR TESTAR DE VERDADE
cont = 0
acely = 3.2
flageranegativo = 0
flagerapositivo = 0
for i in range(50):
    if acely<= -3.2:
        print("entrei no menor")
        acely = acely + 1.6
        flagaumenta = 1
        if flageranegativo:
            flageranegativo = 0
        else:
            flageranegativo = 1
        msg = f"acelx:2.5, acely:{acely}, tempo:{cont/10}\n"
    elif acely>= 3.2:
        print("entrei aqui no maior")
        acely = acely - 1.6
        flagaumenta = 0
        if flagerapositivo:
            flagerapositivo = 0
        else:
            flagerapositivo = 1
        msg = f"acelx:2.5, acely:{acely}, tempo:{cont}\n"
    elif acely == 0:
        if flagerapositivo and not flageranegativo:
            flagaumenta = 1
            acely += 1.6
            msg = f"acelx:2.5, acely:{acely}, tempo:{cont}\n"
        elif flageranegativo and not flagerapositivo:
            flagaumenta = 0
            acely -=1.6
            msg = f"acelx:2.5, acely:{acely}, tempo:{cont}\n"  
        else:
            if flagaumenta:
                acely = acely + 1.6
                msg = f"acelx:2.5, acely:{acely}, tempo:{cont}\n"
            else:
                acely = acely - 1.6
                msg = f"acelx:2.5, acely:{acely}, tempo:{cont}\n"
                    
    else:
        print("entrei no else")
        if flagaumenta:
            acely = acely + 1.6
            msg = f"acelx:2.5, acely:{acely}, tempo:{cont}\n"
        else:
            acely = acely - 1.6
            msg = f"acelx:2.5, acely:{acely}, tempo:{cont}\n"

    ser.write(msg.encode('utf-8'))
    print("Enviado:", msg.strip())
    time.sleep(0.5)
    cont+=1

#função que atualiza o gráfico
def update(frame):
    global x_data, y_data,tempo,acel,vel,pos0,pos,vel0,acel0,tempo0
    #leitura do serial
    if ser.in_waiting > 0:
        try:
            line_read = ser.readline().decode('utf-8').strip()
            if line_read:
                # Tratando a linha com formato: acelx:%f, acely:%f
                partes = line_read.split(',')
                acelx = float(partes[0].split(':')[1])
                acel = float(partes[1].split(':')[1])
                tempototal = float(partes[2].split(':')[1])
                tempo = tempototal - tempo0
                tempo0 = tempototal
                calculavel()
                calculapos()
                acel0 = acel
                vel0 = vel
                pos0 = pos
                print(tempo)
                # encontra a altura

                # Empilha novos dados no array numpy
                y_data = np.append(y_data, pos)
                x_data = np.append(x_data, tempototal)

                line.set_data(x_data, y_data)

                # Ajusta limites do gráfico dinamicamente
                ax.relim()
                ax.autoscale_view()

        except ValueError:
            pass

    return line

ani = FuncAnimation(fig, update, interval=100, cache_frame_data=False)
plt.show()
ser.close()
