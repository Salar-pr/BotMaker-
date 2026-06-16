while True: 

    try:
        n = int(input("enter ypur number:"))
    except:
        print("you can enter only typeint number!!!!!")
        continue
    if n%2 == 0:
        print("is even")
    else:
        print("is odd")

