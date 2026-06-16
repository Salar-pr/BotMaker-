def is_list_empty(list):
    if len(list) == 0 :
        print("your list is empty")
    else:
        print("your list is %d char"%(len(list)))

list = input("enter your list:")
is_list_empty(list)