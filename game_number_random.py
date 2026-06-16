import random

javabe = random.randint(1,99)
hads = int(input("whats your hads?"))
count = 0
while javabe!=hads:
  if hads>javabe:
    print("mine is smmaler")
  else:
    print("mine is bigger")
  hads = int(input("whats your hads?"))
  

  count+=1


print(f"horaaaaaaaaaaa  you try it game {count}" )