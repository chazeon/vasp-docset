import re
from pathlib import Path
from bs4 import BeautifulSoup, Tag
from lxml.html import fromstring
from tqdm.cli import tqdm

DOCSET_ROOT = 'vasp.docset'
DOCSET_DOCS = Path(f'{DOCSET_ROOT}/Contents/Resources/Documents')

if __name__ == "__main__":

    # Input descriptions

    for file in tqdm(list(DOCSET_DOCS.glob("**/*.html"))):

        path = file.relative_to(DOCSET_DOCS)
        soup = BeautifulSoup(open(file), features="lxml")

        for tag in soup.find_all("h2"):
            name = tag.text
            type = "Section"
            anchor = soup.new_tag('a', attrs={'name': f'//apple_ref/cpp/{type}/{name}', 'class':'dashAnchor'})
            tag.insert(0, anchor)

        with open(file, "w") as fp:
            fp.write(str(soup))
