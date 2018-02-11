.PHONY: clean dist

dist:
	python setup.py sdist

install: 
	pip install --upgrade dist/DanaCompiler*

clean:
	rm -rf DanaCompiler.egg-info dist
	find . -name \*.pyc -delete
