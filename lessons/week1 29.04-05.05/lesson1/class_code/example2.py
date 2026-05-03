

#x = "*****#### Hello World &&&$$$$"
#y = x.strip("*#&$ ")
#z = x.lower()
#print(x,y,z)
#print(y)
#print(z)


# _Momi1 = "Tomer Shimoni"
# #_Momi2 = ["Tomer","Shimoni"]
# _Momi2 = _Momi1.split()
# print(_Momi2)
# _Momi2.append("is the best")
# #print(_Momi2)
# for val in _Momi2:
#     print(val[1:4])


_set1 = {1,2,3,4,5}
_set2 = {1,2,3,4,5}
# print(id(_set2))
# print(id(_set1))
_set3 = _set1|_set2
#print(_set3)
_set4 = _set1.union(_set2)
print(_set4)

