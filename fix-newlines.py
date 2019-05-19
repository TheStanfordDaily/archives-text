import os
import re
import fileinput

def get_files():
    years = os.listdir(".")
    for year in filter(os.path.isdir, years):
        if not re.match(r'^\d{4}$', year):
            continue
        for month in os.listdir(year):
            if not os.path.isdir(os.path.join(year, month)): continue
            for day in os.listdir(os.path.join(year, month)):
                if not os.path.isdir(os.path.join(year, month, day)): continue
            files = [os.path.join(year, month, day, file) for file in os.listdir(os.path.join(year, month, day))]
            yield files


for files in get_files():
    for file in files:
        print(file)
        with open(file, "r") as f:
            lines = f.readlines()
        with open(file, "w") as f:
            prefix = "#"
            for line in lines:
                if prefix == "":
                    f.write(line)
                elif prefix == "####":
                    f.write("\n" + line)
                    prefix = ""
                elif line.startswith(prefix):
                    if prefix != "#":
                        f.write("\n")
                    f.write(line.strip("\n"))
                    prefix += "#"
                else:
                    # Should be joined together with the previous line.
                    f.write(" " + line.strip())