import base64
import os
import re
import shutil

MAX_TITLE_LENGTH = 70

years = os.listdir(".")
for year in filter(os.path.isdir, years):
    if not re.match(r'^\d{4}$', year):
        continue
    print(year)
    for month in os.listdir(year):
        if not os.path.isdir(os.path.join(year, month)): continue
        for day in os.listdir(os.path.join(year, month)):
            if not os.path.isdir(os.path.join(year, month, day)): continue
            new_dir = os.path.join(year[:2] + "xx", year[:3] + "x", year + "y", month + "m", day + "d")
            os.makedirs(new_dir, exist_ok=True)
            for filename in os.listdir(os.path.join(year, month, day)):
                file_path = os.path.join(year, month, day, filename)
                with open(file_path, "r", errors='ignore') as file:
                    first_line = file.readline()
                    try:
                        _, title = first_line.split("# ", 1)
                        title = title.strip()[:MAX_TITLE_LENGTH]
                    except ValueError:
                        print("Error parsing first line: {}".format(first_line))
                        title = "Untitled article"
                encoded_title = base64.urlsafe_b64encode(title.encode("utf-8")).decode("utf-8")
                new_path = os.path.join(year, month, day, filename)
                new_filename = filename
                new_filename = re.sub(r'advertisement\.txt$', f"{encoded_title}.advertisement.txt", new_filename)
                new_filename = re.sub(r'article\.txt$', f"{encoded_title}.article.txt", new_filename)
                new_path = os.path.join(new_dir, new_filename)
                # print(file_path, new_path)
                shutil.move(file_path, new_path)
