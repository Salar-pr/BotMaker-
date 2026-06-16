from tkinter import *
import requests

window = Tk()
window.title('Crypto Currency')
window.geometry('400x300')

label1 = Label(window, text='Wellcome')
label1.pack(pady=5)

label2 = Label(window, text='Price : ', fg='blue', bg='cyan')


def get_price():
    symbol1 = input1.get().upper()
    symbol2 = input2.get().upper()
    try:
        url = f'https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ADA,QTUM,SOL,1INCH,eth&tsyms={symbol1}'
        request = requests.get(url)
        data = request.json()
        price = data[symbol2][symbol1]
        # print(data)
        text = f'{symbol2} price is : {price} {symbol1}'

    except:
        text = 'Error!'
    label2.config(text=text)
    label2.place(x=128, y=145)

input1 = Entry(window)
input1.insert(0, 'USD')
input1.pack(pady=5)

input2 = Entry(window)
input2.insert(0, 'BTC')
input2.pack(pady=5)

button = Button(window, text='Get Price', command=get_price)
button.pack(pady=5)

window.mainloop()
