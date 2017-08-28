.PHONY: clean release

test:
	coverage run -m unittest bericht.tests.test_html_css bericht.tests.test_html_table
	coverage xml

clean:
	rm -rf build dist bericht.egg-info .coverage coverage.xml

release:
	python setup.py sdist bdist_wheel upload
