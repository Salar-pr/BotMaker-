li = [1,2,3,4,5]

def aa(num):
    return num ** 2


print(list(map(aa,li)))#مپ برای اعمال کردن فانکشن بر روی تمام ایتم ها

#به توان 2 کردن 


li2= [i*2 for i in range(12) if i%2==0 if i !=0 ]
print(li2)


li3 = (i*j for i in range(10) for j in range(20))

print(list(li3))
