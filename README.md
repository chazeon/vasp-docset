# VASP Docset

[VASP](https://www.vasp.at/) (the Vienna _ab initio_ simulation package) docset for [Dash](http://kapeli.com/dash/).

![](screenshot.png)

## How to scrape and build docset

First, install the required dependencies

```
python3 -m pip install -r requirements.txt
```

then run the scripts

```bash
python3 scriptsa/scrape.py
python3 scriptsa/vaspdoc2set.py
```

## Licence

The code is licenced under the [MIT Licence](LICENCE).
The original document is licenced under [GNU Free Documentation License 1.2](https://www.gnu.org/licenses/old-licenses/fdl-1.2.txt).
