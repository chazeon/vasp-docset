#!/usr/local/bin/python

import os, re, sqlite3
from bs4 import BeautifulSoup
from pathlib import Path

DOCSET_ROOT = 'vasp.docset'

conn = sqlite3.connect(f'{DOCSET_ROOT}/Contents/Resources/docSet.dsidx')
cur = conn.cursor()

try:
    cur.execute('DROP TABLE searchIndex;')
except:
    pass

cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

docpath = Path(f'{DOCSET_ROOT}/Contents/Resources/Documents')

def insert_index(name, type, path):
    print(name, type, path)
    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, type, path))

# Categories

for fname in docpath.glob("Category:*.html"):
    title = re.sub("_", " ", fname.stem)
    title = re.sub("^Category:", "", title)
    insert_index(title, 'Category', str(fname.name))

# INPUT Files

for file in [
    "Category:Files.html",
    "Category:Input_files.html",
    "Category:Output_files.html",
]:
    soup = BeautifulSoup(open(docpath / file), features="lxml")
    for a in soup.select("#category-members > li > a"):
        insert_index(a.text, 'File', a["href"])

    
# INPUT Tags

for file in [
    "Category:INCAR.html",
    "Category:INCAR_tag.html",
    "Category:POTCAR_tag.html",
]:
    soup = BeautifulSoup(open(docpath / file), features="lxml")
    for a in soup.select("#category-members > li > a"):
        name = re.sub(' ', '_', a.text)
        insert_index(name, 'Parameter', a["href"])

# Examples

soup = BeautifulSoup(open(docpath / "Category:Examples.html"), features="lxml")
for a in soup.select("#category-members > li > a"):
    insert_index(a.text, 'Guide', a["href"])

# All

for file in docpath.glob("**/*.html"):
    soup = BeautifulSoup(open(file), features="lxml")
    title = soup.find("title")
    insert_index(title.text, 'Entry', str(file.relative_to(docpath)))


conn.commit()
conn.close()
