def fibonacci():
    number = range(int(input("enter your range for fibonacci namber:")))
    x = 0
    y = 1
    for eche_numbers in number:
        z = x + y
        x = y
        y = z
        print(z)


print(fibonacci())
