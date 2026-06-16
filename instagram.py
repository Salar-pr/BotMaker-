import requests
from datetime import datetime, timedelta

# مقدارهای مورد نیاز را اینجا وارد کنید
ACCESS_TOKEN = "توکن_دسترسی_شما"
INSTAGRAM_BUSINESS_ID = "ایدی_بیزینس_اکانت"

# تاریخ ۷ روز گذشته
since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")

# API برای دریافت لیست پست‌ها
url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_BUSINESS_ID}/media?fields=id,caption,media_type,permalink,timestamp&since={since_date}&access_token={ACCESS_TOKEN}"

response = requests.get(url)
data = response.json()

# دریافت ID پست‌ها
if "data" in data:
    posts = data["data"]
    views_data = []

    for post in posts:
        post_id = post["id"]
        
        # دریافت تعداد بازدیدهای پست
        insights_url = f"https://graph.facebook.com/v18.0/{post_id}/insights?metric=video_views&access_token={ACCESS_TOKEN}"
        insights_response = requests.get(insights_url)
        insights_data = insights_response.json()
        
        if "data" in insights_data and insights_data["data"]:
            views = insights_data["data"][0]["values"][0]["value"]
            views_data.append((post["permalink"], views))

    # مرتب کردن پست‌ها بر اساس بازدید
    sorted_posts = sorted(views_data, key=lambda x: x[1], reverse=True)

    print("\nپست‌های پربازدید هفته اخیر:")
    for i, (link, views) in enumerate(sorted_posts, 1):
        print(f"{i}. {link} - بازدید: {views}")

else:
    print("خطا در دریافت اطلاعات پست‌ها:", data)
