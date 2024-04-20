# app.py

from flask import Flask, render_template

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sozlesme_ekle')
def sozlesme_ekle():
    return render_template('sozlesme_ekle.html')

if __name__ == '__main__':
    app.run(debug=True)

