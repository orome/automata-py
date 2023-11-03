"""
A simple Python (3.10+) implementation aimed at simulating some cellular automata, primarily those focused on by Stephan Wolfram in his book "A New Kind of Science".

Functionality is currently limited to 1D, multi-state, immediate neighbor automata using various boundary conditions.
"""

# USE - Not needed if specified in pyproject.toml
# __author__ = 'Roy Levien' ;

# See - http://www.python.org/dev/peps/pep-0440/
# ^v(0|[1-9]\d*)\.(0|[1-9]\d*)(?:\.(0|[1-9]\d+))?((?:[ab]|rc)(0|[1-9]\d*))?(?:\.(?:dev|post)(0|[1-9]\d*))?$
# USE -
__release__ = '0.1'  # N(.N)*
# USE - To indicate status of release, can be on any branch
__pre_release__ = 'a3'  # aN | bN | rcN
# USE - For all commits on develop branch, never on main branch, increment after each commit (that publishes)
__suffix__ = '.dev19'  # .devN |  (.postN)
__version__ = __release__ + __pre_release__ + __suffix__

from .core import *
