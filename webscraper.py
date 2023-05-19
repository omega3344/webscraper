from bs4 import BeautifulSoup
import requests
import os
from datetime import date
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from dotenv import load_dotenv


#Load environment variables
#load_dotenv()
try:
    #ENV_PASSWORD = os.getenv('PASSWORD')
    #ENV_FROM = os.getenv('FROM')
    #ENV_TO = os.getenv('TO')
    ENV_FROM = os.environ['FROM']
    ENV_PASSWORD = os.environ['PASSWORD']
    ENV_TO = os.environ['TO']
except KeyError:
    raise KeyError('Token not available!')


#Notify price via email
def send_email(price, msg):
    message = MIMEMultipart("alternative")
    message["Subject"] = msg + str(date.today().strftime("%d-%m-%Y"))
    message["From"] = ENV_FROM
    message["To"] = ENV_TO

    html = f'''
        <html>
        <head>
        </head>
        <body>
            <p>Olá,<br><br>
            O atual preço médio mensal da eletricidade no mercado indexado é de  
            <strong>{price}€/MWh</strong>.
            </p>
        </body>
        </html>
        '''
    
    message.attach(MIMEText(html, 'html'))

    #Create secure connection with server and send email
    context = ssl.create_default_context()
    port = 465 #for SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login(ENV_FROM, ENV_PASSWORD)
        server.sendmail(ENV_FROM, ENV_TO.split(','), message.as_string())


#main

URL = 'https://datahub.ren.pt/pt/eletricidade/mercado/'
page_text = requests.get(URL, verify=False).text
soup = BeautifulSoup(page_text, 'lxml')
data = soup.find_all('span', class_='center-cell')
price = data[4].text

if float(price) > 200:
    msg = 'ATENÇÃO! Preço médio acima de 200€/MWh! - '
else:
    msg = 'Preço médio do MWh - '

send_email(price, msg)
