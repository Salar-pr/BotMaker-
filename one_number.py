
def find_number():
    li =[]

    for i in range(2,50):
        flag = True
        for num in range(2,i):
            if i % num == 0:
                flag = False
                break
        if flag:
            li.append(i)

    print(li)

