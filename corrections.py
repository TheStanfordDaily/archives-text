import xml.etree.ElementTree as ET
import os
import re
import fileinput
from tqdm import tqdm

PATH = "./stanford-text-corrections/stanford"

def create_corrections():
    years = os.listdir(PATH)
    for year in filter(os.path.isdir, years):
        for directory in os.listdir(os.path.join(PATH, year)):
            for (dirname, year, month, day) in re.findall(r'((\d{4})(\d{2})(\d{2})-\d{2})', directory):
                tqdm.write(dirname) 
                path = os.path.join(PATH, year, dirname + ".dir", f"stanford{dirname}-changes.log")
                with open(path) as f:
                    xml = f.read()
                tree = ET.fromstring("<root>" + xml + "</root>")
                # print(tree, year, month, day)
                corrections = []
                files = [os.path.join(year, month, day, file) for file in os.listdir(os.path.join(year, month, day))]
                for textCorrectedBlock in tree:
                    blockID = textCorrectedBlock.attrib["blockID"]
                    corrections = {} 
                    for textCorrectedLine in textCorrectedBlock:
                        oldTextValue = textCorrectedLine.findtext("OldTextValue")
                        newTextValue = textCorrectedLine.findtext("NewTextValue").strip()
                        corrections[oldTextValue] = newTextValue
                yield files, corrections

for files, corrections in tqdm(create_corrections()):
    if len(corrections) == 0:
        continue
    with fileinput.input(files=(files), inplace=True) as f:
        for line in f:
            if line.strip() in corrections:
                print(corrections[line.strip()])
                del corrections[line.strip()]
            else:
                print(line)
    break
