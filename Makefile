NAME='vasp'
DOCSET="vasp.docset"

clean:
	rm ${DOCSET}/Contents/Resources/Documents/*.html

vasp.tgz: vasp.docset
	tar --exclude='.DS_Store' -cvzf $@ $<