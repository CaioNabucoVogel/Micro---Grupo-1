import numpy as np
import time 
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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
ax.set_ylim(-2, 2)
ax.set_xlabel("Tempo")
ax.set_ylabel("Altura")

#script de teste local COMENTAR QUANDO FOR TESTAR DE VERDADE
cont = 0
for i in range(10):
    msg = f"acelx:2.5, acely:3.2, tempo:{cont}\n"
    ser.write(msg.encode('utf-8'))
    print("Enviado:", msg.strip())
    time.sleep(0.5)
    cont+=1

#função que atualiza o gráfico
def update(frame):
    global x_data, y_data

    #leitura do serial
    if ser.in_waiting > 0:
        try:
            line_read = ser.readline().decode('utf-8').strip()
            if line_read:
                # Tratando a linha com formato: acelx:%f, acely:%f
                partes = line_read.split(',')
                acelx = float(partes[0].split(':')[1])
                acely = float(partes[1].split(':')[1])
                tempo = float(partes[2].split(':')[1])
                print(tempo)
                # encontra a altura

                # Empilha novos dados no array numpy
                y_data = np.append(y_data, acelx)
                x_data = np.append(x_data, tempo)

                line.set_data(x_data, y_data)

                # Ajusta limites do gráfico dinamicamente
                if len(x_data) > ax.get_xlim()[1]:
                    ax.set_xlim(0, len(x_data) + 10)

        except ValueError:
            pass

    return line

ani = FuncAnimation(fig, update, interval=100, cache_frame_data=False)
plt.show()
ser.close()
