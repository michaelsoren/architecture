from distutils.core import setup
from Cython.Build import cythonize

setup(name='cache-simulator',
      ext_modules=cythonize("cython_address.pyx"))
