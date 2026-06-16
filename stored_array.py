li = [1,1,2]
x = []
for i in set(li):
    x.append(i)

count=len(li) - len(set(li))
for i in range(count):
    x.append("_")


print(x)

