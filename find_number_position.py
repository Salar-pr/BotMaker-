def find_number_position(matrix, number):
    for i, row in enumerate(matrix):
        if number in row:
            return (i, row.index(number))
    return None

# مثال استفاده
matrix = [
    [10, 20, 30],
    [40, 50, 60],
    [70, 80, 90]
]

number = 50
position = find_number_position(matrix, number)

if position:
    print(f"عدد {number} در مکان {position} قرار دارد.")
else:
    print(f"عدد {number} در جدول یافت نشد.")