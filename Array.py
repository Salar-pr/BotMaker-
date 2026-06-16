import random

# تابع برای ساخت جدول اعداد تصادفی


def create_random_table(row, column, a, b):
    # ایجاد لیست اعداد تصادفی
    # هیچ کدام از اعداد تکراری پشت سر هم قرار نگرفته اند
    my_list = []
    size = row * column
    while len(my_list) < size:
        num = random.randint(a, b)
        if len(my_list) == 0 or num != my_list[-1]:
            my_list.append(num)
        else:
            for _ in range(10):
                num = random.randint(a, b)
                if num != my_list[-1]:
                    my_list.append(num)
                    break
                else:
                    continue

    # چاپ جدول
    for i in range(0, len(my_list), column):
        print(str(my_list[i:i + column]))
    return my_list

# تابع برای یافتن مختصات اعداد تکرار شده


def find_occurrences(my_list, n, row, column):
    occurrences = [(i // column, i % column)
                   for i, x in enumerate(my_list) if x == n]
    return occurrences
# تعداد تکراری بودن عدد


def count_list(my_list, n):
    return my_list.count(n)

    print({count_list(my_list, n)})


# دریافت ورودی‌ها از کاربر
row = int(input("enter your row: "))
column = int(input("enter your cole: "))
a = int(input("enter your start rang random:"))
b = int(input("enter your end rang random:"))

# ایجاد جدول و یافتن مختصات اعداد تکرار شده
my_list = create_random_table(row, column, a, b)
n = int(input("enter your number for serche :"))
occurrences = find_occurrences(my_list, n, row, column)

# چاب تعداد تکرار
print(count_list(my_list, n))
# چاپ مختصات
for occ in occurrences:
    print(f"row {occ[0] + 1}, column {occ[1] + 1}")
