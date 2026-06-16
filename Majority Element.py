nums = [2,2,1,1,1,2,2]
condedate = 0
vote = 0
for n in nums:
    if vote==0:
        condedate = n
    if condedate==n:
        vote+=1
    else:
        vote-=1

print(condedate)
