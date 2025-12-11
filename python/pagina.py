## Página do flask que mostra o simulador de onda# app.py
from flask import Flask, Response, render_template
from leitor import GraficoAltura

app = Flask(__name__)

grafico = GraficoAltura("loop://")  # use sua porta real aqui

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(grafico.stream(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
