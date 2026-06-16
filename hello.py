payment = int(input("enter your salary:"))
tax = 0
if 0 <= payment <= 5000 :
   print(payment - tax)
elif 5000 <= payment <= 8000 :
   tax = payment/100*10
   
   print(payment - tax)
elif 8000<= payment <= 12000 :
   tax = payment/100*20

   print(payment - tax)
else:
   print("nothing")





#z = 5
#print("zoj") if z % 2 == 0 else print("fard")




#for pz in range(5):
#    for pi in range(pz):
#        print(pz,end=" #")
#        print()


# a = [1,2,3,4,5]
# index = 0
# while index < len(a):
#     print(a[index])
#     index += 1