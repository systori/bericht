|pypi| |travis| |grade| |issues| |coverage|

=======
bericht
=======

Incremental HTML to PDF converter with support for extremely large documents. Bericht does not
hold the HTML or the PDF in memory as it generates PDF pages; instead, it requires you to pass a
generator which produces HTML snippets and **bericht** gives you a PDF stream iterator. As you iterate
the PDF stream **bericht** will parse just enough HTML to produce a single page and return one page
at a time which you can either write to a file, send over http or do whatever you need.

Main features:

 - Quickly and efficiently generate on-demand PDFs from databases or other data sources.

 - Use familiar HTML and CSS to define your PDF layout.

 - Re-use the same code to produce HTML and PDF based reports for your users.

 - Ability to generate extremely large PDF files without storing any of the parts (input or output) in memory.

 - Many CSS extensions specifically for print/page related formatting:

   - ``@page:nth-child(an+b)``: at-rule to target/style individual pages (non-standard CSS).

   - ``@page { letterhead-page: 1; }``: ability to apply specific pages from another PDF as a
     watermark/letterhead in your newly generated PDF (the other PDF must be passed as argument
     to **bericht** generator to be able to extract pages from it using ``letterhead-page`` CSS attribute).

   - ``thead:nth-child(an+b)`` and ``tfoot:nth-child(an+b)``: **bericht** can repeat table headers/footers
     on subsequent pages when the table does not fit on one page, this rule allows you to style those
     rows differently depending on what page they are on (non-standard CSS).


.. |pypi| image:: https://badge.fury.io/py/bericht.svg
   :target: https://pypi.python.org/pypi/bericht
   :alt: Package

.. |travis| image:: https://travis-ci.org/systori/bericht.svg?branch=master
   :target: https://travis-ci.org/systori/bericht
   :alt: Build

.. |grade| image:: https://codeclimate.com/github/systori/bericht/badges/gpa.svg
   :target: https://codeclimate.com/github/systori/bericht
   :alt: Code Climate

.. |issues| image:: https://codeclimate.com/github/systori/bericht/badges/issue_count.svg
   :target: https://codeclimate.com/github/systori/bericht
   :alt: Issue Count

.. |coverage| image:: https://codeclimate.com/github/systori/bericht/badges/coverage.svg
   :target: https://codeclimate.com/github/systori/bericht/coverage
   :alt: Test Coverage
