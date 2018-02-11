.PHONY: clean dist

dist:
	python setup.py sdist

install: 
	pip3 install --upgrade dist/DanaCompiler*

clean:
	rm -rf DanaCompiler.egg-info dist
	find . -name \*.pyc -delete
