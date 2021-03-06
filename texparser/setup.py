#
# The MIT License (MIT)
# 
# Copyright (c) 2019 Philippe Faist
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import os.path
#import sys

from setuptools import setup, find_packages

from texparser.version import version_str

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name = "texparser",
    version = version_str,

    # metadata for upload to PyPI
    author = "Markus Näther",
    author_email = "naetherm@informatik.uni-freiburg.de",
    description = "Simple LaTeX parser providing latex-to-unicode and unicode-to-latex conversion originally developed by Philippe Faist.",
    long_description = read("README.md"),
    license = "MIT",
    keywords = "latex text unicode encode parse expression",
    url = "https://github.com/phfaist/pylatexenc",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup :: LaTeX',
    ],

    # files
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'texwalker=texparser.texwalker.__main__:main',
            'tex2text=texparser.tex2text.__main__:main',
            'texsimplifier=texparser.texsimplifier.__main__:main',
            'texmacroexpander=texparser.texmacroexpander.__main__:main',
            'textpostwork=texparser.textpostwork.__main__:main',
        ],
    },
    install_requires = [],
    package_data = {
    },
)