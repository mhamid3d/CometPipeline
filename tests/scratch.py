from collections import defaultdict


mydict = defaultdict({'pass': None, 'errorMsg': None, 'description': None})

mydict['Yessir']['pass'] = False

print(mydict)