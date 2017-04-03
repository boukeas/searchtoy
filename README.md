# searchtoy
Searchtoy is a python 3 library for solving combinatorial search problems.

The library is currenty under development and its interface _should not be
considered stable_.

The code in this repository includes many well-documented examples of using
the library to solve typical combinatorial search problems. You can follow
them through to see how you can use the library to solve your own search
problems.

In a nutshell, building a program to solve a search problem essentially
involves building a class to hold the problem _state representation_ and then
building a _generator_ to define how new states can be created from existing
one, by applying operators. Optionally, you can also build heuristic
_evaluators_ to help guide the search.

Searchtoy originated as a personal project, with an intent to experiment with
the characteristics of the python language while building a library that could
actually do something useful. Therefore the library's code can also act as a
showcase for several python idioms such as generators, decorators and
metaclasses.

The searchtoy code is licensed under the
[MIT License](https://github.com/boukeas/sherlock/blob/master/LICENSE).

## Why use this library?

## Things you might want to check out

## Installing searchtoy

Start by cloning this [github repository](https://github.com/boukeas/searchtoy.git) or
simply download the [.zip file](https://github.com/boukeas/searchtoy/archive/master.zip)
and extract it.

``cd`` into the directory containing ``searchtoy``'s code and install it.

    pip install .

If you like, you can install ``searchtoy`` in a virtual environment. Before installing,
create and activate the environment:

    virtualenv ~/environments/searchtoy
    source ~/environments/searchtoy/bin/activate

Here, ``~/environments/searchtoy`` is the directory where the virtual environment
will be installed. You can modify this as you please. Play around and, when you 're
done, deactivate the virtual environment.

    deactivate

The library will eventually be made available through the Python Package Index.
