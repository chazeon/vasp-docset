import re, sqlite3
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional

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
    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, type, path))

def find_by_name(name) -> list:
    cur.execute('SELECT * FROM searchIndex WHERE (name = ?)', (name,))
    return cur.fetchall()

def find_by_path(path) -> list:
    cur.execute('SELECT * FROM searchIndex WHERE (path = ?)', (path,))
    return cur.fetchall()

def get_page_title(file) -> Optional[str]:
    if Path(file).exists():
        soup = BeautifulSoup(open(file), features="lxml")
        title = soup.find("title")
        return title.text

if __name__ == "__main__":

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
            title = get_page_title(docpath / a["href"])
            if title:
                insert_index(title, 'File', a["href"])

    # INPUT Tags

    for file in [
        "Category:INCAR.html",
        "Category:INCAR_tag.html",
        "Category:POTCAR_tag.html",
    ]:
        soup = BeautifulSoup(open(docpath / file), features="lxml")
        for a in soup.select("#category-members > li > a"):
            title = get_page_title(docpath / a["href"])
            if title:
                insert_index(title, 'Parameter', a["href"])

    # Examples

    soup = BeautifulSoup(open(docpath / "Category:Examples.html"), features="lxml")
    for a in soup.select("#category-members > li > a"):
        title = get_page_title(docpath / a["href"])
        if title:
            insert_index(title, 'Guide', a["href"])

    # All

    for file in docpath.glob("**/*.html"):
        title = get_page_title(file)
        path = str(file.relative_to(docpath))
        if len(find_by_path(path)) == 0 and title:
            insert_index(title, 'Entry', path)


    conn.commit()
    conn.close()
