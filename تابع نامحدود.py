def addder(*a): # به تور نامحدود میتوان ارگومان قرارذ داد
    return a

print(addder(1,2,3,4,5,6))



def addder(**a): # به طور key value داده گذاری میشوند
    return a

print(addder(i="d",g="h"))


