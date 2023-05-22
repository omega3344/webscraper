from bs4 import BeautifulSoup
import requests
import os
from datetime import date
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


#Load environment variables
load_dotenv()
try:
    ENV_PASSWORD = os.getenv('PASSWORD')
    ENV_FROM = os.getenv('FROM')
    ENV_TO = os.getenv('TO')
    #ENV_FROM = os.environ['FROM']
    #ENV_PASSWORD = os.environ['PASSWORD']
    #ENV_TO = os.environ['TO']
except KeyError:
    raise KeyError('Token not available!')

#Calculate invoice total
def calc_total(price):
    ER = 370
    PMD = price/1000
    Desv = 0.004
    PT = 1.1507
    FA = 1.02
    CG = ER*0.005
    TP = ER*-0.0958
    POT = 30*0.229
    
    total = round(ER*(PMD+Desv)*PT*FA+CG+TP+POT,2)
    
    return total

#Notify price via email
def send_email(price, msg, total):
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
            <br>
            Para um consumo médio de 370kW é estimado um total de fatura de 
            <strong>{total}€</strong>.
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

URL = 'http://datahub.ren.pt/pt/eletricidade/mercado/'
page_text = requests.get(URL).text
soup = BeautifulSoup(page_text, 'lxml')
data = soup.find_all('span', class_='center-cell')
price = float(data[4].text)

if price > 200:
    msg = 'ATENÇÃO! Preço médio acima de 200€/MWh! - '
else:
    msg = 'Preço médio do MWh - '

send_email(price, msg, calc_total(price))
