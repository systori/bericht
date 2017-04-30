.PHONY: clean release

clean:
	rm -rf build dist bericht.egg-info

release:
	python setup.py sdist bdist_wheel upload
