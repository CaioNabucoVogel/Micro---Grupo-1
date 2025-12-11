import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from leitor import GraficoAltura


class AppGUI:

    def __init__(self):
        # Cria janela
        self.root = tk.Tk()
        self.root.title("Interface de Usuário")

        # Instancia seu objeto de leitura (COM / loop)
        self.graf = GraficoAltura('loop://', 9600,1)
        self.graf.teste()
        print("fim do teste")

        # ------- FRAME DO GRÁFICO -------
        frame_graf = tk.Frame(self.root)
        frame_graf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        print("frame")

        # Embed da figure no Tkinter
        self.canvas = FigureCanvasTkAgg(self.graf.fig, master=frame_graf)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        print("embed feito")

        # Cria animação do Matplotlib rodando no Tkinter
        self.ani = FuncAnimation(
            self.graf.fig,
            self.graf.update,
            interval=100,
            cache_frame_data=False
        )

        print("animaçao concluida")

        # ------- FRAME DAS INFORMAÇÕES -------
        frame_info = tk.Frame(self.root)
        frame_info.pack(side=tk.RIGHT, fill=tk.Y)

        # Texto com valor de altura
        self.label_pico = tk.Label(frame_info, text="Pico: --", font=("Arial", 16))
        self.label_pico.pack(pady=10)

        # Atualizador do label de altura (loop no Tkinter)
        self.update_label()

        # ------- IMAGEM -------
        imagem = Image.open("python/images/oceanica.png")  # coloque uma imagem na pasta
        imagem = imagem.resize((250, 250))
        self.img_tk = ImageTk.PhotoImage(imagem)

        label_img = tk.Label(frame_info, image=self.img_tk)
        label_img.pack(pady=10)

    def update_label(self):
        """Atualiza texto de altura em tempo real."""
        try:
            if not self.root.winfo_exists():
                return

            if hasattr(self.graf, "pico"):
                self.label_pico.config(text=f"Pico: {self.graf.pico:.2f}")

            # chama novamente em 200ms
            self.root.after(200, self.update_label)
        except tk.TclError:
            return

    def run(self):
        self.root.mainloop()

    def on_close(self):
        # Cancela eventos after antes de destruir a janela
        try:
            self.root.after_cancel(self._after_id)
        except:
            pass

        self.root.destroy()


if __name__ == "__main__":
    app = AppGUI()
    app.run()
    app.on_close()
