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
    
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
            
def ekle_firma(firma_adi, telefon, firma_yetkilisi, firma_yetkilisi_email):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "INSERT INTO firma (firma_adi, telefon, firma_yetkilisi, firma_yetkilisi_email) VALUES (%s, %s, %s, %s)"
        values = (firma_adi, telefon, firma_yetkilisi, firma_yetkilisi_email)
        cursor.execute(sql, values)
        connection.commit()
        print("firma eklendi")
    
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
            
def ekle_ilgilifirma(ilgili_firma_adi, ilgili_firma_telefon, ilgili_firma_email, ilgili_firma_yetkilisi, ilgili_firma_yetkilisi_email):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "INSERT INTO ilgili_firma (ilgili_firma_adi, ilgili_firma_telefon, ilgili_firma_email, ilgili_firma_yetkilisi, ilgili_firma_yetkilisi_email) VALUES (%s, %s, %s, %s, %s)"
        values = (ilgili_firma_adi, ilgili_firma_telefon, ilgili_firma_email, ilgili_firma_yetkilisi, ilgili_firma_yetkilisi_email)
        cursor.execute(sql, values)
        connection.commit()
        print("ilgili firma eklendi")
    
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
            
def get_firma_id(firma_adi):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "SELECT firma_id FROM firma WHERE firma_adi = %s"
        cursor.execute(sql, (firma_adi))
        firma_id = cursor.fetchone()[0]  # İlk sütundaki değeri alıyoruz
        
        return firma_id
    
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_departman_id(departman_adi):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "SELECT departman_id FROM departman WHERE departman_adi = %s"
        cursor.execute(sql, (departman_adi))
        departman_id = cursor.fetchone()[0]  # İlk sütundaki değeri alıyoruz
        
        return departman_id
    
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_ilgili_firma_id(ilgili_firma_adi):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "SELECT ilgili_firma_id FROM ilgili_firma WHERE ilgili_firma_adi = %s"
        cursor.execute(sql, (ilgili_firma_adi,))
        ilgili_firma_id = cursor.fetchone()[0]  # İlk sütundaki değeri alıyoruz
        
        return ilgili_firma_id
    
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

            
            

def get_kullanici_id(email):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "SELECT id FROM kullanici WHERE email = %s"
        cursor.execute(sql, (email))
        kullanici_id = cursor.fetchone()[0]  # İlk sütundaki değeri alıyoruz
        
        return kullanici_id
    
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def ekle_sozlesme(sozlesme_basligi, email, firma_adi, departman_adi, ilgili_firma_adi, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # Firma, departman ve ilgili firma id'lerini al
        cursor.execute("SELECT id FROM kullanici WHERE email = %s", (email,))
        kullanici_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT firma_id FROM firma WHERE firma_adi = %s", (firma_adi,))
        firma_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT departman_id FROM departman WHERE departman_adi = %s", (departman_adi,))
        departman_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT ilgili_firma_id FROM ilgili_firma WHERE ilgili_firma_adi = %s", (ilgili_firma_adi,))
        ilgili_firma_id = cursor.fetchone()[0]
        
        sql = """INSERT INTO sozlesme (sozlesme_basligi, kullanici_id, firma_id, departman_id, ilgili_firma_id, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama)
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        values = (sozlesme_basligi, kullanici_id, firma_id, departman_id, ilgili_firma_id, sozlesme_icerigi, sozlesme_kodu, imza_yetkilisi, aciklama)
        
        cursor.execute(sql, values)
        connection.commit()
        print("Sözleşme eklendi")
    
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

            
def get_sozlesme_id(sozlesme_kodu):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        sql = "SELECT sozlesme_id FROM sozlesme WHERE sozlesme_kodu = %s"
        cursor.execute(sql, (sozlesme_kodu))
        sozlesme_id = cursor.fetchone()[0]  # İlk sütundaki değeri alıyoruz
        
        return sozlesme_id
    
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
        
def ekle_sozlesme_bilgileri(sozlesme_bilgileri_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # Sözleşme kodunu kullanarak sözleşme ID'sini al
        sozlesme_bilgileri_id = get_sozlesme_id(sozlesme_bilgileri_id)
        
        # Sözleşme bilgilerini ekleme
        sql = "INSERT INTO sozlesme_bilgileri (sozlesme_bilgileri_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (sozlesme_bilgileri_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati)
        cursor.execute(sql, values)
        connection.commit()
        print("Sözleşme bilgileri eklendi")
        
    except mysql.connector.Error as err:
        print("Hata: ", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Sözleşme ekleme formu için GET ve POST taleplerini işleyen view fonksiyonu
@app.route('/add-sozlesme', methods=['POST'])
def save_sozlesme():
    
        try:
            data = request.json
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
            firma_adi= data['firma_adi']
            telefon= data['telefon']
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
            
            
            ekle_departman(departman_adi, departman_email)
            ekle_firma(firma_adi, telefon, firma_yetkilisi, firma_yetkilisi_email)
            ekle_ilgilifirma(ilgili_firma_adi, ilgili_firma_telefon, ilgili_firma_email, ilgili_firma_yetkilisi, ilgili_firma_yetkilisi_email)
            
            #kullanici_id = get_kullanici_id(session['email'])
            #firma_id = get_firma_id(firma_adi)
            #departman_id = get_departman_id(departman_adi)
            ilgili_firma_id = get_ilgili_firma_id(ilgili_firma_adi)
            print (ilgili_firma_id)
            #ekle_sozlesme()


            #sozlesme_bilgileri_id = get_sozlesme_id(sozlesme_kodu)


            ekle_sozlesme_bilgileri(sozlesme_bilgileri_id, baslangic_tarihi, bitis_tarihi, bilgilendirme_amaci, bilgilendirme_tipi, bilgilendirme_tarihi, bilgilendirme_saati)

            
            return jsonify({"message": "sözlşeme başarıyla eklendi"}), 200
        except Exception as e:
        # Hata durumunda yanıt gönder
           return jsonify({"message": "sözleşme eklenirken bir hata oluştu"}), 500
    
    
    
    
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