import requests
from bs4 import BeautifulSoup
import jinja2
import re
from tqdm.cli import tqdm
from pathlib import Path
import requests_cache

DOCSET_ROOT = 'vasp.docset'

def get_wiki_api(params):
    PARAMS={"format":"json"}
    URL = "https://www.vasp.at/wiki/api.php"
    S = requests.Session()
    requests_cache.install_cache('cache')
    params = {**PARAMS, **params}
    R = S.get(url=URL, params=params)
    return R.json()[params['action']]

def get_allpages(**kwargs):
    return get_wiki_api({
        "action": "query",
        "list": "allpages",
        "aplimit": "max",
        **kwargs
    })

def get_allcategories(**kwargs):
    return get_wiki_api({
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


page_template = open("templates/page.html").read()
page_template = template = jinja2.Template(page_template)

def scrape_page(**kwargs):

    page_data = get_wiki_api({
        "action": "parse",
        **kwargs
    })
    title = page_data["title"]
    content = page_data['text']['*']

    # categories
    categorieshtml = get_wiki_api({
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


category_template = open("templates/category.html").read()
category_template = jinja2.Template(category_template)

def get_category_members(**kwargs):
    return get_wiki_api({
        "action": "query",
        "list": "categorymembers",
        "cmlimit": "max",
        **kwargs
    })

def scrape_category_page(**kwargs):

    try:
        page_data = get_wiki_api({
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


apfrom = None
pages = []

for category in tqdm(get_allcategories()["allcategories"]):
    scrape_category_page(page=f'Category:{category["*"]}')

while True:
    tmp = get_allpages(apfrom=apfrom)["allpages"]
    pages.extend(tmp[1:])
    if len(tmp) == 1:
        break
    else:
        apfrom = tmp[-1]["title"]

for page in tqdm(pages):
    scrape_page(pageid=page["pageid"])

    if len(pages) < 500:
        break


    # scrape_page(pageid=page["pageid"])