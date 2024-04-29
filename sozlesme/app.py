from flask import Flask, render_template, request, jsonify, redirect, session, url_for, flash, get_flashed_messages
import mysql.connector
from time import sleep
import bcrypt
import re

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
        
def check_password(sifre):
    # En az 5 en fazla 8 karakter kontrolü
    if len(sifre) < 5 or len(sifre) > 8:
        return False
    
    # Büyük harf kontrolü
    if not re.search("[A-Z]", sifre):
        return False
    
    # Küçük harf kontrolü
    if not re.search("[a-z]", sifre):
        return False
    
    # Sembol kontrolü
    if not re.search("[.+/=-_:;!@#$%^&*?]", sifre):
        return False
    
    return True

def add(isim, soyisim, sifre, email):
    try:
        connection = connect()
        cursor = connection.cursor()
        hashed_sifre = bcrypt.hashpw(sifre.encode('utf-8'), bcrypt.gensalt())
        
        sql = "INSERT INTO kullanici (isim, soyisim, sifre, email) VALUES (%s, %s, %s, %s)"
        values = (isim, soyisim, hashed_sifre.decode('utf-8'), email)
        cursor.execute(sql, values)
        connection.commit()
        print("Kullanıcı eklendi")
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        kullanici_id = cursor.fetchone()[0]
        print("Eklenen kullanıcının ID'si:", kullanici_id)
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
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

@app.route('/hesabim.html', methods=['GET'])
def hesabim():
    return render_template('hesabim.html') 

@app.route('/sozlesmelerim', methods=['GET'])
def sozlesmelerim():
    return render_template('sozlesmelerim.html')


@app.route('/add-endpoint', methods=['POST'])
def add_kullanici():
    try:
        # Gelen JSON verisini al
        data = request.json
        connection = connect()
        cursor = connection.cursor()
        
        # Gelen JSON'un eksik olup olmadığını kontrol et
        if 'isim' not in data or 'soyisim' not in data or 'sifre' not in data or 'email' not in data:
            return jsonify({"message": "Eksik parametreler"}), 400
        
        # Kullanıcı bilgilerini almak
        isim = data['isim']
        soyisim = data['soyisim']
        sifre = data['sifre']
        email = data['email']
        
        if not check_password(sifre):
            return jsonify({"message": "Şifre en az 5 en fazla 8 karakter olmalı, büyük harf, küçük harf ve sembol içermelidir."}), 400
        
        # Email kontrolü yap
        
        cursor.execute("SELECT email FROM kullanici WHERE email = %s", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            return jsonify({"message": "Bu email adresi zaten kullanılmaktadır."}), 400
        
        # Veritabanına ekleme
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
            
            # Kullanıcı adını session'a kaydet
            session['username'] = user[3]
            session['soyisim'] = user[4]
            session['email'] = user[2]
            session['sifre'] = user[1]
            session['kullanici_id'] = user[0]
            
            kullanici_id = user[0]
            print("Giriş yapan kullanıcının ID'si:", kullanici_id)
            
       
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


# Diğer yönlendirmeler
def ekle_departman(departman_adi, departman_email):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "INSERT INTO departman (departman_adi, departman_email) VALUES (%s, %s)"
        values = (departman_adi, departman_email)
        cursor.execute(sql, values)
        connection.commit()
        print("departman eklendi")
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        departman_id = cursor.fetchone()[0]
        print("Eklenen departmanın ID'si:", departman_id)
    
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            
            
            
def ekle_firma(firma_adi, telefon, firma_yetkilisi, firma_yetkilisi_email):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "INSERT INTO firma (firma_adi, telefon, firma_yetkilisi, firma_yetkilisi_email) VALUES (%s, %s, %s, %s)"
        values = (firma_adi, telefon, firma_yetkilisi, firma_yetkilisi_email)
        cursor.execute(sql, values)
        connection.commit()
        print("firma eklendi")
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        firma_id = cursor.fetchone()[0]
        print("Eklenen firmanın ID'si:", firma_id)
    
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            
            
            
def ekle_ilgilifirma(ilgili_firma_adi, ilgili_firma_telefon, ilgili_firma_email, ilgili_firma_yetkilisi, ilgili_firma_yetkilisi_email):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "INSERT INTO ilgili_firma (ilgili_firma_adi, ilgili_firma_telefon, ilgili_firma_email, ilgili_firma_yetkilisi, ilgili_firma_yetkilisi_email) VALUES (%s, %s, %s, %s, %s)"
        values = (ilgili_firma_adi, ilgili_firma_telefon, ilgili_firma_email, ilgili_firma_yetkilisi, ilgili_firma_yetkilisi_email)
        cursor.execute(sql, values)
        connection.commit()
        print("ilgili firma eklendi")
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        ilgili_firma_id = cursor.fetchone()[0]
        print("Eklenen ilgili firmanın ID'si:", ilgili_firma_id)
    
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            
                        

def ekle_sozlesme(sozlesme_basligi, email, firma_adi, departman_adi, ilgili_firma_adi, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # SQL sorgusunda JOIN(tabloları birleştiriyor) kullanarak gerekli bilgileri alıyoruz
        sql = """
        INSERT INTO sozlesme (sozlesme_basligi, kullanici_id, firma_id, departman_id, ilgili_firma_id, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama)
        SELECT %s, k.kullanici_id, f.firma_id, d.departman_id, i.ilgili_firma_id, %s, %s, %s, %s
        FROM kullanici k
        JOIN firma f ON k.email = %s AND f.firma_adi = %s
        JOIN departman d ON d.departman_adi = %s
        JOIN ilgili_firma i ON i.ilgili_firma_adi = %s
        """
        
        values = (sozlesme_basligi, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama, email, firma_adi, departman_adi, ilgili_firma_adi)
        
        # Sorguyu çalıştırma ve değişiklikleri kaydetme kodu
        cursor.execute(sql, values)
        connection.commit()
        
        sozlesme_id = cursor.lastrowid
        print("Sözleşme eklendi, ID:", sozlesme_id)
        
        print("Sözleşme eklendi")
    
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()            
        
def ekle_sozlesme_bilgileri(sozlesme_kodu, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # Sözleşme bilgilerini eklemek için sözleşme ID'sini alıyoruz
        cursor.execute("SELECT sozlesme_id FROM sozlesme WHERE sozlesme_kodu = %s", (sozlesme_kodu,))
        sozlesme_id = cursor.fetchone()[0]
        print ("Sözleşme ID:", sozlesme_id)
        
        # Sözleşme bilgilerini ekleme sorgusu
        sql = "INSERT INTO sozlesme_bilgileri (sozlesme_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (sozlesme_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati)
        cursor.execute(sql, values)
        connection.commit()
        print("Sözleşme bilgileri eklendi")
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()


# Sözleşme ekleme formu için GET ve POST taleplerini işleyen view fonksiyonu

@app.route('/add-sozlesme', methods=['POST'])
def save_sozlesme():
    try:
        data = request.json

        # Kullanıcının oturum bilgilerini aldık
        email = session.get('email')

        if not email:
            return jsonify({"message": "Oturum açılmamış kullanıcı"}), 401

        # Formdan gelen verileri aldık
        baslangic_tarihi = data['baslangic_tarihi']
        bitis_tarihi = data['bitis_tarihi']
        bilgilendirme_amaci = data['bilgilendirme_amaci']
        bilgilendirme_tipi = data['bilgilendirme_tipi']
        bilgilendirme_tarihi = data['bilgilendirme_tarihi']
        bilgilendirme_saati = data['bilgilendirme_saati']
        sozlesme_kodu = data['sozlesme_kodu']
        imza_yetkilisi = data['imza_yetkilisi']
        aciklama = data['aciklama']
        firma_adi = data['firma_adi']
        telefon = data['telefon']
        firma_yetkilisi = data['firma_yetkilisi']
        firma_yetkilisi_email = data['firma_yetkilisi_email']
        ilgili_firma_adi = data['ilgili_firma_adi']
        ilgili_firma_telefon = data['ilgili_firma_telefon']
        ilgili_firma_email = data['ilgili_firma_email']
        ilgili_firma_yetkilisi = data['ilgili_firma_yetkilisi']
        ilgili_firma_yetkilisi_email = data['ilgili_firma_yetkilisi_email']
        sozlesme_basligi = data['sozlesme_basligi']
        sozlesme_icerigi = data['sozlesme_icerigi']
        departman_adi = data['departman_adi']
        departman_email = data['departman_email']

        # Firma, departman ve ilgili firma bilgilerini ekledik
        ekle_departman(departman_adi, departman_email)
        ekle_firma(firma_adi, telefon, firma_yetkilisi, firma_yetkilisi_email)
        ekle_ilgilifirma(ilgili_firma_adi, ilgili_firma_telefon, ilgili_firma_email, ilgili_firma_yetkilisi, ilgili_firma_yetkilisi_email)

        # Eklenen bilgileri kullanarak sözleşmeyi ekliyoruz
        connection = connect()
        cursor = connection.cursor()

        # Sözleşme ekleme SQL sorgusu
        sql = """
        INSERT INTO sozlesme (sozlesme_basligi, kullanici_id, firma_id, departman_id, ilgili_firma_id, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama)
        SELECT %s, k.kullanici_id, f.firma_id, d.departman_id, i.ilgili_firma_id, %s, %s, %s, %s
        FROM kullanici k
        JOIN firma f ON k.email = %s AND f.firma_adi = %s
        JOIN departman d ON d.departman_adi = %s
        JOIN ilgili_firma i ON i.ilgili_firma_adi = %s
        """

        values = (sozlesme_basligi, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama, email, firma_adi, departman_adi, ilgili_firma_adi)

        # Sorguyu çalıştırma kodu ve değişiklikleri kaydetme kodu
        cursor.execute(sql, values)
        connection.commit()

        # Eklenen sözleşmenin ID'sini alıyoruz
        sozlesme_id = cursor.lastrowid
        print("Sözleşme eklendi, ID:", sozlesme_id)
    
        # Sözleşme bilgilerini ekledik
        sql_sozlesme_bilgileri = """
        INSERT INTO sozlesme_bilgileri (sozlesme_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values_sozlesme_bilgileri = (sozlesme_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati)
        cursor.execute(sql_sozlesme_bilgileri, values_sozlesme_bilgileri)
        connection.commit()
        
        return jsonify({"message": "Sözleşme başarıyla eklendi", "sozlesme_id": sozlesme_id}), 200
    except Exception as e:
        # Hata durumunda dönen yanıt
        return jsonify({"message": "Sözleşme eklenirken bir hata oluştu"}), 500

    
def delete_user(email):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # Kullanıcıyı silme sorgusu
        sql = "DELETE FROM kullanici WHERE email = %s"
        cursor.execute(sql, (email,))
        connection.commit()
        print("Kullanıcı silindi")
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
            

@app.route('/delete-account', methods=['POST'])
def delete_account():
    try:
        # Kullanıcı oturum bilgilerinden e-posta adresini aldık
        email = session.get('email')
        
        if not email:
            return jsonify({"message": "Kullanıcı oturumu bulunamadı."}), 401
        
        # Kullanıcıyı veritabanından sildik
        delete_user(email)
        
        # Oturumu sonlandır
        session.clear()
        
        # Başarı durumunda yanıt gönderdik
        return jsonify({"message": "Kullanıcı başarıyla silindi"}), 200
    except Exception as e:
        # Hata durumunda yanıt gönderdik
        return jsonify({"message": "Kullanıcı silinirken bir hata oluştu"}), 500



@app.route('/change-password', methods=['POST'])
def change_password():
    try:
        # Yeni şifre ve kullanıcı adını aldık
        new_password = request.form['new_password']
        username = session['username']
        
        # Veritabanında kullanıcıyı güncelledik
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE kullanici SET sifre = %s WHERE isim = %s", (new_password, username))
        connection.commit()
        
        # Başarılı mesajını gösterdik
        return jsonify({"message": "Şifre başarıyla değiştirildi.", "sifre": new_password}), 200

    except Exception as e:
        # Hata durumunda yanıt gönderdik
        return jsonify({"message": "Şifre değiştirme sırasında bir hata oluştu."}), 500
    
    


@app.route('/get_data', methods=['GET'])
def get_data():
    try:
         connection = connect()
    
        
         if connection.is_connected():
            print("Connected to MySQL database")
            
            # Kullanıcı ID'sini aldık
            kullanici_id = session.get('kullanici_id')
            # Veritabanından verileri aldık
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT s.sozlesme_id, s.kullanici_id, f.firma_adi, d.departman_adi, il.ilgili_firma_adi, 
        s.sozlesme_basligi, s.sozlesme_icerigi, s.sozlesme_kodu, s.imza_yetkilisi, s.aciklama, 
        sb.baslangic_tarihi, sb.bitis_tarihi, sb.bilgilendirme_amaci, sb.bilgilendirme_tipi, 
        sb.bilgilendirme_tarihi, sb.bilgilendirme_saati
        FROM sozlesme s
        LEFT JOIN firma f ON s.firma_id = f.firma_id
        LEFT JOIN departman d ON s.departman_id = d.departman_id
        LEFT JOIN ilgili_firma il ON s.ilgili_firma_id = il.ilgili_firma_id
        LEFT JOIN sozlesme_bilgileri sb ON s.sozlesme_id = sb.sozlesme_id
        WHERE s.kullanici_id = %s
            """
            cursor.execute(query, (kullanici_id,))
            data = cursor.fetchall()  # Tüm sözleşmeleri almak için fetchall() kullandık
            return jsonify(data)
        
        
    except Exception as e:
        print("Error getting data from MySQL database:", e)
        return jsonify({'error': str(e)}), 500
    
    
    

from flask import request, jsonify

@app.route('/delete_contract', methods=['POST'])
def delete_contract():
    try:
        # İstekten sözleşme ID'lerini aldık
        contract_ids = request.form.getlist('sozlesme_ids')
        
        # Sözleşmeleri sozlesme_bilgileri tablosundan sildik
        connection = connect()
        cursor = connection.cursor()
        for contract_id in contract_ids:
            # Sözleşmeyi sozlesme_bilgileri tablosundan sildik
            delete_query = "DELETE FROM sozlesme_bilgileri WHERE sozlesme_id = %s"
            cursor.execute(delete_query, (contract_id,))
            
            # Sözleşmeyi sozlesme tablosundan da sildik
            delete_query = "DELETE FROM sozlesme WHERE sozlesme_id = %s"
            cursor.execute(delete_query, (contract_id,))
        
        connection.commit()
        
        return jsonify({'message': 'Seçilen sözleşmeler başarıyla silindi.'}), 200
    except Exception as e:
        return jsonify({'error': 'Sözleşmeler silinirken bir hata oluştu: ' + str(e)}), 500





            
        
    

    
    
if __name__ == '__main__':
    app.run(debug=True) 