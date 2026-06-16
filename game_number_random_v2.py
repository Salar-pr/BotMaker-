import random

a = 1
b = 99

hads = random.randint(a,b)
print(hads)

javab=input("smmaler or bigger or true?")

while javab!="true":
  if javab=="s":
    b=hads-1
    a=a
  elif javab=="b":
    a=hads+1
    b=b
  hads = random.randint(a,b)
  print(hads)
  javab=input("smmaler or bigger or true?")

print("wowww")
    


