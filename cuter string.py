x = """altgraph==0.17.4
anyio==4.3.0
asgiref==3.8.1
certifi==2024.2.2
charset-normalizer==3.3.2
contourpy==1.2.1
cycler==0.12.1
Django==5.0.7
djangorestframework==3.15.2
fonttools==4.53.1
h11==0.14.0
httpcore==1.0.3
httpx==0.26.0
idna==3.6
Khayyam==3.0.17
kiwisolver==1.4.5
matplotlib==3.9.1
mysql-connector==2.2.9
mysql-connector-python==8.4.0
mysqlclient==2.2.4
networkx==3.3
numpy==2.0.0
opencv-python==4.10.0.84
packaging==24.1
pefile==2023.2.7
pillow==10.4.0
pyinstaller==6.9.0
pyinstaller-hooks-contrib==2024.7
PyMySQL==1.1.1
pyparsing==3.1.2
pyTelegramBotAPI==4.16.1
python-bidi==0.6.0
python-dateutil==2.9.0.post0
python-telegram-bot==20.8
pywin32-ctypes==0.2.2
requests==2.31.0
rtl==0.4.3
schedule==1.2.2
six==1.16.0
sniffio==1.3.0
sqlparse==0.5.1
telebot==0.0.5
tzdata==2024.1
urllib3==2.2.1"""


def cuter(str):
    x = str.split('\n')
    for i in x:
        l = i.index('==')
        print(i[:l])
cuter(x)
