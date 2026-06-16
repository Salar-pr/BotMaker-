def Arrangement(_from, _to, stop_size):
    i = _from
    while i > _to:
        print(i)
        i += stop_size


_from = int(input("enter from:"))
_to = int(input("enter to:"))
stop_size = int(input("enter stop_size:"))
Arrangement(_from, _to, stop_size)
