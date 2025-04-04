import json
import os

home = "/home/esad/Desktop/college_work/SEPM/project/"

ls = os.listdir(home+"jsons")
files = [f for f in ls if os.path.isfile(home+'jsons/'+f)]

for i in files:
    with open(home+'jsons/'+i, "r") as file:
        data = json.load(file)
    
    deps = data["deps"]
    dep_names = []
    for j in deps:
        dep_names.append(j['name'])
    to_dump = {
        "name": data["name"],
        "deps": dep_names,
    }
    print(to_dump)

    with open(home+'jsons/cleaned/'+i, "w") as file:
        json.dump(to_dump, file, indent=4)
    print(i, "updated successfully!")
