import os

parent_dir = "./hasil_augmentasi"

dir_name = 'A'

for i in range(26):
    path = os.path.join(parent_dir, dir_name)
    dir_name = chr(ord(dir_name) + 1)
    
    os.mkdir(str(path))
    