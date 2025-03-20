import os

home = "/home/esad/Desktop/college_work/SEPM/project/"

ls = os.listdir(home+"jsons")
files = [f for f in ls if os.path.isfile(home+'jsons/'+f)]

for i in files:
    with open(home+'jsons/'+i, "r+") as file:
        content = file.read()
        o_count = 0
        c_count = 0
        c_ind = 0
        for j in range(len(content)):
            i = content[j]
            if (i == "{"):
                o_count += 1
            if (i == "}"):
                c_count += 1
            if (o_count - c_count) == 0:
                c_ind = j
                break

        file.seek(0)
        file.write(content[:c_ind+1])
        file.truncate()
