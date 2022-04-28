import re
from pathlib import Path

from tqdm.cli import tqdm

import requests
import requests_cache
import jinja2
from bs4 import BeautifulSoup

DOCSET_ROOT = 'vasp.docset'

class MWAPI():

    URL = "https://www.vasp.at/wiki/api.php"
    CACHE = 'cache'

    def __init__(self) -> None:
        self.session = requests_cache.CachedSession(self.CACHE)

    def get(self, params):
        params = {
            'format': 'json',
            **params
        }
        response = self.session.get(url=self.URL, params=params)
        return response.json()[params['action']]

mwapi = MWAPI()

def get_allpages(**kwargs):
    return mwapi.get({
        "action": "query",
        "list": "allpages",
        "aplimit": "max",
        **kwargs
    })

def get_allcategories(**kwargs):
    return mwapi.get({
        "action": "query",
        "list": "allcategories",
        "aclimit": "max",
        **kwargs
    })

def get_link(title):
    file = re.sub(r" ", r"_", title)

def clean_html(content):
    soup = BeautifulSoup(content, features="lxml")

    for a in soup.findAll('a'):
        try:
            a['href'] = re.sub(r'^/wiki/index.php/(.*)$', r'\1.html', a['href'])
            a['href'] = re.sub(r'^Category:', r'Category%3A', a['href'])
        except:
            pass
    
    for el in soup.select(".mw-editsection"):
        el.decompose()
    
    return str(soup)


page_template = jinja2.Template(open("templates/page.html").read())

def scrape_page(**kwargs):

    page_data = mwapi.get({
        "action": "parse",
        **kwargs
    })
    title = page_data["title"]
    content = page_data['text']['*']

    # categories
    categorieshtml = mwapi.get({
        "action": "parse",
        "prop": "categorieshtml",
        **kwargs
    })["categorieshtml"]["*"]

    file = re.sub(r" ", r"_", title)
    path = Path(f'{DOCSET_ROOT}/Contents/Resources/Documents/{file}.html')
    path.parent.mkdir(exist_ok=True)

    with open(path, 'w') as fp:
        fp.write(page_template.render({
            "title": page_data["displaytitle"],
            "content": clean_html(content),
            "categorieshtml": clean_html(categorieshtml)
        }))


category_template = jinja2.Template(open("templates/category.html").read())

def get_category_members(**kwargs):
    return mwapi.get({
        "action": "query",
        "list": "categorymembers",
        "cmlimit": "max",
        **kwargs
    })

def scrape_category_page(**kwargs):

    try:
        page_data = mwapi.get({
            "action": "parse",
            **kwargs
        })
        title = page_data["title"]
        content = page_data['text']['*']
    except:
        title = kwargs["page"]
        content = ""

    members = get_category_members(cmtitle=kwargs["page"])["categorymembers"]
    for member in members:
        link = re.sub(' ', '_', member["title"])
        link = re.sub(r'^Category:', r'Category%3A', link)
        member["link"] = link

    file = re.sub(r" ", r"_", title)
    path = Path(f'{DOCSET_ROOT}/Contents/Resources/Documents/{file}.html')
    path.parent.mkdir(exist_ok=True)

    with open(path, 'w') as fp:
        fp.write(category_template.render({
            "title": title,
            "content": clean_html(content),
            "members": members
        }))


if __name__ == "__main__":

    # Get 'Category:xxx' pages

    for category in tqdm(get_allcategories()["allcategories"]):
        scrape_category_page(page=f'Category:{category["*"]}')

    # Get entry-page list

    apfrom = None
    pages = []

    while True:
        tmp = get_allpages(apfrom=apfrom)["allpages"]
        pages.extend(tmp[1:])
        if len(tmp) == 1:
            break
        else:
            apfrom = tmp[-1]["title"]

    # Get entry pages

    for page in tqdm(pages):
        scrape_page(pageid=page["pageid"])

        if len(pages) < 500:
            break