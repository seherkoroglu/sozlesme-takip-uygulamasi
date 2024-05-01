import getpass
import smtplib
from datetime import datetime, timedelta
import pytz
from flask import Flask, render_template, request, jsonify, redirect, session, url_for, flash, get_flashed_messages

import mysql.connector
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from time import sleep
import bcrypt
import re
import os

HOST = "smtp-mail.outlook.com"
PORT = 587

FROM_EMAIL = "a@gmail.com"
PASSWORD = os.getenv("EMAIL_PASSWORD")

# Kullanıcıdan alınan e-posta adresi
TO_EMAIL = input("Enter recipient email address: ")

smtp = smtplib.SMTP(HOST, PORT)

status_code, response = smtp.ehlo()

print(f"[*] Echoing the server: {status_code} {response}")

status_code, response = smtp.starttls()

status_code, response = smtp.login(FROM_EMAIL, PASSWORD)

app = Flask(__name__, static_folder='static')
import os
app.secret_key = os.urandom(24)

def connect():
    try:
        connection = mysql.connector.connect(
            host='localhost', user='root', password='root', database='sozlesme_takip', port='3306'
        )
        return connection
    except mysql.connector.Error as err:
        print("Hata: ", err)
        
def send_reminder_email(reminder_type, reminder_datetime):
    local_tz = pytz.timezone('Europe/Istanbul')  # Kullanıcının zaman dilimine göre ayarla
    reminder_datetime = local_tz.localize(reminder_datetime)

    if reminder_type == 'Günlük':
        if reminder_datetime <= datetime.now(local_tz):
            smtp.sendmail(FROM_EMAIL, TO_EMAIL, f"Daily reminder: {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    elif reminder_type == 'Haftalık':
        # Haftalık hatırlatma
        reminder_day = reminder_datetime.weekday()
        current_day = datetime.now(local_tz).weekday()
        if reminder_datetime <= datetime.now(local_tz):
            reminder_datetime += timedelta(days=(7 - (current_day - reminder_day) % 7))
            smtp.sendmail(FROM_EMAIL, TO_EMAIL, f"Weekly reminder: {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    elif reminder_type == 'Aylık':
        # Aylık hatırlatma
        current_month = datetime.now(local_tz).month
        reminder_month = reminder_datetime.month
        if current_month != reminder_month:
            smtp.sendmail(FROM_EMAIL, TO_EMAIL, f"Monthly reminder: {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

# Önce veritabanından sözleşme bilgilerini alalım
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
            
            for row in data:
                reminder_date_str = row['bilgilendirme_tarihi']
                reminder_time_str = row['bilgilendirme_saati']
                reminder_type = row['bilgilendirme_tipi']
                
                # Tarih ve saati birleştirerek datetime nesnesine dönüştür
                reminder_datetime = datetime.strptime(reminder_date_str + ' ' + reminder_time_str, '%Y-%m-%d %H:%M:%S')
                send_reminder_email(reminder_type, reminder_datetime)

            return jsonify(data)


    except Exception as e:
        print("Error getting data from MySQL database:", e)
        return jsonify({'error': str(e)}), 500




