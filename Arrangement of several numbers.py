def Arrangement(_from, _to, stop_size):
    for number in range(_from, _to, stop_size):
        print(number)


_from = int(input("enter from:"))
_to = int(input("enter to:"))
stop_size = int(input("enter stop_size:"))
Arrangement(_from, _to, stop_size)
