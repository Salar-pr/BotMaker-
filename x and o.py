jadval = [0,1,2,3,4,5,6,7,8]
def create_X_O_table(jadval):
    
    

    for i in range(0, len(jadval), 3):
        

        print(jadval[i:i + 3])
    return jadval 

create_X_O_table(jadval)
count = 0
while True:
    
    count += 1

    if count % 2 == 0:
        a = int(input(" X enter your x: "))
        
        c = a

        jadval[c] = "X"
        
    else:
        a = int(input(" O enter your o: "))
        
        c = a
        jadval[c] = "O"
    create_X_O_table(jadval)

    if jadval[0] == "X" and jadval[1] == "X" and jadval[2] == "X":
        print("X win")
        break
    if jadval[0] == "X" and jadval[3] == "X" and jadval[6] == "X":
        print("X win")
        break
    if jadval[0] == "X" and jadval[4] == "X" and jadval[8] == "x":
        print("X win")
        break
    if jadval[1] == "X" and jadval[4] == "X" and jadval[7] == "X":
        print("X win")
        break
    if jadval[2] == "X" and jadval[4] == "X" and jadval[6] == "X":
        print("X win")
        break
    if jadval[2] == "X" and jadval[5] == "X" and jadval[8] == "X":
        print("X win")
        break
    if jadval[3] == "X" and jadval[4] == "X" and jadval[5] == "X":
        print("X win")
        break
    if jadval[6] == "X" and jadval[7] == "X" and jadval[8] == "X":
        print("X win")
        break
    


    if jadval[0] == "O" and jadval[1] == "O" and jadval[2] == "O":
        print("O win")
        break
    if jadval[0] == "O" and jadval[3] == "O" and jadval[6] == "O":
        print("O win")
        break
    if jadval[0] == "O" and jadval[4] == "O" and jadval[8] == "O":
        print("O win")
        break
    if jadval[1] == "O" and jadval[4] == "O" and jadval[7] == "O":
        print("O win")
        break
    if jadval[2] == "O" and jadval[4] == "O" and jadval[6] == "O":
        print("O win")
        break
    if jadval[2] == "O" and jadval[5] == "O" and jadval[8] == "O":
        print("O win")
        break
    if jadval[3] == "O" and jadval[4] == "O" and jadval[5] == "O":
        print("O win")
        break
    if jadval[6] == "O" and jadval[7] == "O" and jadval[8] == "O":
        print("O win")
        break
    