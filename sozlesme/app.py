from flask import Flask, render_template, request, jsonify, redirect, session, url_for, flash, get_flashed_messages
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
            # Kullanıcı adını session'a kaydet
            session['username'] = user[3]
            session['soyisim'] = user[4]
            session['email'] = user[2]
            session['sifre'] = user[1]
            
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


# Diğer route'lar
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
        
        # SQL sorgusunda JOIN kullanarak gerekli bilgileri al
        sql = """
        INSERT INTO sozlesme (sozlesme_basligi, kullanici_id, firma_id, departman_id, ilgili_firma_id, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama)
        SELECT %s, k.kullanici_id, f.firma_id, d.departman_id, i.ilgili_firma_id, %s, %s, %s, %s
        FROM kullanici k
        JOIN firma f ON k.email = %s AND f.firma_adi = %s
        JOIN departman d ON d.departman_adi = %s
        JOIN ilgili_firma i ON i.ilgili_firma_adi = %s
        """
        
        values = (sozlesme_basligi, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama, email, firma_adi, departman_adi, ilgili_firma_adi)
        
        # Sorguyu çalıştır ve değişiklikleri kaydet
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
        
        # Sözleşme bilgilerini eklemek için sözleşme ID'sini al
        cursor.execute("SELECT sozlesme_id FROM sozlesme WHERE sozlesme_kodu = %s", (sozlesme_kodu,))
        sozlesme_id = cursor.fetchone()[0]
        print ("Sözleşme ID:", sozlesme_id)
        
        # Sözleşme bilgilerini ekleme
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

        # Kullanıcının oturum bilgilerini al
        email = session.get('email')

        if not email:
            return jsonify({"message": "Oturum açılmamış kullanıcı"}), 401

        # Formdan gelen verileri al
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

        # Firma, departman ve ilgili firma bilgilerini ekleyelim
        ekle_departman(departman_adi, departman_email)
        ekle_firma(firma_adi, telefon, firma_yetkilisi, firma_yetkilisi_email)
        ekle_ilgilifirma(ilgili_firma_adi, ilgili_firma_telefon, ilgili_firma_email, ilgili_firma_yetkilisi, ilgili_firma_yetkilisi_email)

        # Eklenen bilgileri kullanarak sözleşmeyi ekleyelim
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

        # Sorguyu çalıştır ve değişiklikleri kaydet
        cursor.execute(sql, values)
        connection.commit()

        # Eklenen sözleşmenin ID'sini alalım
        sozlesme_id = cursor.lastrowid
        print("Sözleşme eklendi, ID:", sozlesme_id)
    
        # Sözleşme bilgilerini ekleyelim
        sql_sozlesme_bilgileri = """
        INSERT INTO sozlesme_bilgileri (sozlesme_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values_sozlesme_bilgileri = (sozlesme_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati)
        cursor.execute(sql_sozlesme_bilgileri, values_sozlesme_bilgileri)
        connection.commit()
        
        return jsonify({"message": "Sözleşme başarıyla eklendi", "sozlesme_id": sozlesme_id}), 200
    except Exception as e:
        # Hata durumunda yanıt gönder
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
        # Kullanıcı oturum bilgilerinden e-posta adresini al
        email = session.get('email')
        
        if not email:
            return jsonify({"message": "Kullanıcı oturumu bulunamadı."}), 401
        
        # Kullanıcıyı veritabanından sil
        delete_user(email)
        
        # Oturumu sonlandır
        session.clear()
        
        # Başarı durumunda yanıt gönder
        return jsonify({"message": "Kullanıcı başarıyla silindi"}), 200
    except Exception as e:
        # Hata durumunda yanıt gönder
        return jsonify({"message": "Kullanıcı silinirken bir hata oluştu"}), 500



@app.route('/change-password', methods=['POST'])
def change_password():
    try:
        # Yeni şifre ve kullanıcı adını al
        new_password = request.form['new_password']
        username = session['username']
        
        # Veritabanında kullanıcıyı güncelle
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE kullanici SET sifre = %s WHERE isim = %s", (new_password, username))
        connection.commit()
        
        # Başarılı mesajını göster
        return jsonify({"message": "Şifre başarıyla değiştirildi.", "sifre": new_password}), 200

    except Exception as e:
        # Hata durumunda yanıt gönder
        return jsonify({"message": "Şifre değiştirme sırasında bir hata oluştu."}), 500
    

    
    

if __name__ == '__main__':
    app.run(debug=True)