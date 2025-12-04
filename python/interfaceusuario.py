import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from leitor import GraficoAltura

def display_graph(fig : GraficoAltura):
    root = tk.Tk()
    root.title("Gráfico Animado com Tkinter")
    
    # Configura o canvas do Matplotlib dentro da interface Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Exibe o gráfico
    canvas.draw()

    # Inicia o loop do Tkinter
    root.mainloop()

# Inicia a interface
if __name__ == "__main__":
    fig = GraficoAltura('loop://')
    fig.teste()
    fig.execute()
    display_graph(fig)