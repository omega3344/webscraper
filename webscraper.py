from bs4 import BeautifulSoup
import requests
import os
from datetime import date
import smtplib, ssl
import urllib3
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
def calc_total(price_m):
    ER = 300
    PMD = price_m/1000
    TAR = 0.0365
    Desv = 0.0065
    PT = 1.1581
    FA = 1.02
    CG = ER*0.005
    TP = ER*TAR
    POT = 30*0.4388
    TTS = 30*0.002893
    AV = 2.85
    DGEG = 0.07
    IEC = ER*0.001

    if ER > 100:
        subtotal6 = 100*(PMD+Desv)*PT*FA+100*0.005+100*TAR+TTS+AV
        subtotal23 = ((ER-100)*(PMD+Desv)*PT*FA+(ER-100)*0.005+(ER-100)*TAR+POT)
    else:
        subtotal6 = ER*(PMD+Desv)*PT*FA+ER*0.005+ER*-0.0121+AV+TTS
        subtotal23 = POT  

    IVA = subtotal6*0.06+(subtotal23+AV+DGEG+IEC)*0.23

    total = round(subtotal6+subtotal23+IVA+DGEG+IEC,2)
    
    return total

#Notify price via email
def send_email(price_d, price_m, msg, total):
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
            O atual preço diário da eletricidade no mercado indexado é de  
            <strong>{price_d}€/MWh</strong>, enquanto o preço médio do mês é de 
            <strong>{price_m}€/MWh</strong>.
            <br>
            Para um consumo médio de 300kW é estimado um total de fatura de 
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

URL = 'https://datahub.ren.pt/pt/eletricidade/mercado/'

try:
    page_text = requests.get(URL, timeout=5).text
except requests.exceptions.RequestException:
    raise Exception('Failed to connect to %s' % URL) from None

soup = BeautifulSoup(page_text, 'html.parser')
data = soup.find_all('strong')

price_d = float(data[0].text[:-5])
price_m = float(data[3].text[:-5])

if price_m > 100:
    msg = 'ATENÇÃO! Preço médio acima de 150€/MWh! - '
else:
    msg = 'Preço médio do MWh - '

send_email(price_d, price_m, msg, calc_total(price_m))
