rg = int(input("enter your range fibonacci:"))
li = []
for i in range(rg):
    if i in [0,1]:
        li.append(1)
    else:
        li.append(li[-1]+li[-2])

print(li)