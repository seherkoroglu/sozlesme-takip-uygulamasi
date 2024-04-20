from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, get_flashed_messages
import mysql.connector
from time import sleep

app = Flask(__name__, static_folder='static')
import os
app.secret_key = os.urandom(24)


# Configure MySQL

def connect():
    try:
        connection = mysql.connector.connect(
            host='localhost', user='root', password='root', database='sozlesme_takip', port='3306'
        )
        return connection
    except mysql.connector.Error as err:
        print("Hata: ", err)

def add(isim, soyisim, sifre, email):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "INSERT INTO kullanici (isim, soyisim, sifre, email) VALUES (%s, %s, %s, %s)"
        values = (isim, soyisim, sifre, email)
        cursor.execute(sql, values)
        connection.commit()
        print("Kullanıcı eklendi")
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/add-endpoint', methods=['POST'])
def add_kullanici():
    try:
        # Gelen JSON verisini al
        data = request.json
        
        # Gelen JSON'un eksik olup olmadığını kontrol et
        if 'isim' not in data or 'soyisim' not in data or 'sifre' not in data or 'email' not in data:
            return jsonify({"message": "Eksik parametreler"}), 400
        
        # Kullanıcı bilgilerini al
        isim = data['isim']
        soyisim = data['soyisim']
        sifre = data['sifre']
        email = data['email']
        
        # Veritabanına ekleme işlemi
        add(isim, soyisim, sifre, email)
        
        # Başarı durumunda yanıt gönder
        return jsonify({"message": "Kullanıcı başarıyla eklendi"}), 200
    except Exception as e:
        # Hata durumunda yanıt gönder
        return jsonify({"message": "Kullanıcı eklenirken bir hata oluştu"}), 500
    
@app.route('/login', methods=['POST'])
def login():
    connection = None 
    try:
       email = request.form['email']
       password = request.form['password']
        
        # Veritabanında kullanıcıyı sorgula
       connection = connect()
       cursor = connection.cursor()
       cursor.execute("SELECT * FROM kullanici WHERE email = %s AND sifre = %s", (email, password))
       user = cursor.fetchone()
        
       if user:
            # Eğer kullanıcı bulunduysa, giriş yap ve ana sayfaya yönlendir
            flash('Giriş başarılı.', 'success')
            return redirect(url_for('sozlesme_ekle'))
       else:
            # Eğer kullanıcı bulunamadıysa veya şifre yanlışsa, hata mesajı göster
            flash('Hatalı e-posta veya şifre, lütfen tekrar deneyin.', 'danger')
            return redirect(url_for('index'))
        
    except mysql.connector.Error as err:
        print("Hata: ", err)
        flash('Giriş sırasında bir hata oluştu, lütfen daha sonra tekrar deneyin.', 'danger') 
        return redirect(url_for('index'))
    finally:
        if connection is not None:
            connection.close()


# Diğer route'lar
@app.route('/')
def index():
    messages = get_flashed_messages()
    return render_template('index.html', messages=messages)

@app.route('/uye_ol', methods=['GET'])
def uye_ol():
    return render_template('uye_ol.html')

@app.route('/sozlesme_ekle', methods=['GET'])
def sozlesme_ekle():
    return render_template('sozlesme_ekle.html')



if __name__ == '__main__':
    app.run(debug=True)
