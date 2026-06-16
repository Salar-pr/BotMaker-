import requests

# مسیر صحیح API
url = "https://min-api.cryptocompare.com/data/price"

# پارامترها: ارز موردنظر و ارز مقصد
params = {
    "fsym": "BTC",  # ارز اصلی (Bitcoin)
    "tsyms": "USD"  # تبدیل به دلار
}

# ارسال درخواست GET
response = requests.get(url, params=params)

# بررسی پاسخ API
if response.status_code == 200:
    print(response.json())  # نمایش قیمت بیت‌کوین به دلار
else:
    print("خطا:", response.status_code, response.text)  # نمایش متن خطا در صورت وجود
