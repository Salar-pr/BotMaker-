def append_list(list1,list2):
    for item in list2:
        list1.append(list2)

        return list1
    
list1 = [1,2,3,4]
list2 = [5,6,7,8]

print(append_list(list1,list2))