import getpass
import smtplib

HOST="smtp-mail.outlook.com"
PORT=587

FROM_EMAIL=""
TO_EMAIL=""
password=getpass.getpass("enter password:")

MESSAGE="Hello"

smtp=smtplib.SMTP(HOST,PORT)

status_code,response=smtp.ehlo()

print(f"[*]Echoing the server: [status_code][response]")

status_code,response=smtp.starttls()

status_code,response=smtp.login(FROM_EMAIL,password)

smtp.sendmail(FROM_EMAIL,TO_EMAIL,MESSAGE)
smtp.quit()

