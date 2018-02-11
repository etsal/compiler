.PHONY: clean dist

dist:
	python setup.py sdist

clean:
	rm -rf DanaCompiler.egg-info dist
