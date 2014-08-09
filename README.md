SOS CoAP is a Python-based CoAP library. Single-threaded; uses Python's asyncore module for non-blocking UDP communication.

Prerequisites
-------------
* Python 2 or 3. Minimum versions unknown, but certainly 2.7 and 3.4.
* pytest and flexmock to run unit tests
* sphinx to build documentation

Installation
------------
Use the standard `python setup.py install`. Supports running unit tests prior to installation with `python setup.py test`.

Get Started
===========
See the `examples` and `test` directories for code that uses the library. For more specifics, build the library documentation from the `doc` directory with:

    $ make html

Then browse `doc/_build/html/index.html`.

Use `test/runtests` to run the unit tests.


Status
======
In early development; no tagged release yet.

Feature  | Comment
-------- | -------
Message type | Non-confirmable and confirmable
Request code | GET, POST, PUT
Options      | Uri-Path, Content-Format; does not support option delta or length > 12

Authors
=======
[Ken Bannister][1]

License
=======
LGPLv3 for the library itself, and MPL for non-library example and test code. Our intent is that "the work" we have developed must remain freely available. For the LGPL library code, you must share any changes you redistribute, and for the MPL non-library code, you must share any changes to those individual files that you redistribute. Please send us your fixes and improvements so everyone benefits!

We're not using the GPL. It's perfectly fine to import the LGPL package/modules, or use an MPL file, in a proprietary application that you redistribute, within the minimal requirements of LGPL and MPL.

[1]: http://cytheric.net