## BF JIT interpreter based on PyPy
rpython tutorial

## Build
```
git submodule --init --update --recursive

$> (python|pypy) pypy/rpython/bin/rpython --opt=jit interpreter.py
```
