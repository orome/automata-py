"""
A brief description of the automata package.

A longer description of the automata package.

.. note::
    Any additional note.
"""

# See - http://www.python.org/dev/peps/pep-0440/
# __author__ = 'Roy Levien'
__release__ = '0.1'  # N(.N)*
__pre_release__ = 'a2'  # aN | bN | cN |
__suffix__ = '.dev001'  # .devN | | .postN
__version__ = __release__ + __pre_release__ + __suffix__

from .core import *

# TBD - Add doc comments and package notes to this file <<<
