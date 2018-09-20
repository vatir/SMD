# Import = list()
# from os import listdir
# for filename in listdir('.'):
#     if not ('__init__' in filename):
#         for ext in {'py', 'pyc'}:
#             if filename.endswith(ext) and not (filename.rstrip(ext)[:-1] in Import):
#                 Import.append(filename.rstrip(ext)[:-1])
#  
# for ToImport in Import:
#     Module = __import__(ToImport)
#     for Member in dir(Module):
#         globals()[Member] = getattr(Module, Member)
