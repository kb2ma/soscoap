from   setuptools import setup
from   setuptools.command.test import test as TestCommand
import sys

# To read __version__
version = {}
with open("./soscoap/version.py") as fp:
    exec(fp.read(), version)

# Allows running unit tests prior to installation with:
#    $ python setup.py test
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name             = 'soscoap',
    version          = version['__version__'],
    description      = 'Constrained Application Protocol (CoAP) library',
    long_description = 'Constrained Application Protocol (CoAP) library',

    packages         = ['soscoap'],
    install_requires = [],
    tests_require    = ['pytest', 'flexmock'],
    cmdclass         = {'test': PyTest},
    
    author       = 'Ken Bannister',
    author_email = 'cytheric@runbox.com',
    url          = 'http://github.com/kb2ma/soscoap',
    license      = 'GNU Lesser General Public License v3 (LGPLv3)',
    classifiers  = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        ],
)