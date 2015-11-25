===============================
Transit CLI Tool
===============================

.. image:: https://img.shields.io/pypi/v/transito.svg
        :target: https://pypi.python.org/pypi/transito

.. image:: https://img.shields.io/travis/marianoguerra/transito.svg
        :target: https://travis-ci.org/marianoguerra/transito

.. image:: https://readthedocs.org/projects/transito/badge/?version=latest
        :target: https://readthedocs.org/projects/transito/?badge=latest
        :alt: Documentation Status


Command Line Tool to Work with Transit Format

* Free software: ISC license
* Documentation: https://transito.readthedocs.org.

Features
--------

* convert to and form json, edn, transit
* read content from stdin or files

Usage
-----

::

    $ transito -h
    usage: transito [-h] {t2j,j2t,e2t,t2e,http} ...

    Transit CLI

    positional arguments:
      {t2j,j2t,e2t,t2e,http}
        t2j                 convert transit to json
        j2t                 convert json to transit
        e2t                 convert edn to transit
        t2e                 convert transit to edn
        http                make http requests with transit data

    optional arguments:
      -h, --help            show this help message and exit

Conversions
...........

Convert Transit to JSON from a file::

    $ transito t2j examples/ex1.transit

    [":keyword", "~lala", 1, 1.2, true, null, [], ["hi", "a"]]

Convert Transit to JSON from stdin::

    $ transito t2j -

    ["~#list",["~:keyword","~$lala",1,1.2,true,null,[],["hi",["~#char","a"]]]]
    [":keyword", "~lala", 1, 1.2, true, null, [], ["hi", "a"]]

.. note::

    The first line is the input, then I pressed Enter and Ctrl+D

Piping from another command::

    $ echo '["~#list",["~:keyword","~$lala",1,1.2,true,null,[],["hi",["~#char","a"]]]]' | transito t2j -

    [":keyword", "~lala", 1, 1.2, true, null, [], ["hi", "a"]]

Same for Edn::

    $ transito t2e examples/ex1.transit

    (keyword lala 1 1.2 true nil [] ["hi" \a])

::

    $ echo '["~#list",["~:keyword","~$lala",1,1.2,true,null,[],["hi",["~#char","a"]]]]' | transito t2e -

    (keyword lala 1 1.2 true nil [] ["hi" \a])

::

    $ transito t2e -

    ["~#list",["~:keyword","~$lala",1,1.2,true,null,[],["hi",["~#char","a"]]]]
    (keyword lala 1 1.2 true nil [] ["hi" \a])

you should get the idea, some with transit as output just in case::

    $ transito e2t -
    (keyword lala 1 1.2 true nil [] ["hi" \a])
    ["~#list",["~$keyword","~$lala",1,1.2,true,null,[],["hi",["~#char","a"]]]]

    $ transito t2j -
    ["~#list",["~$keyword","~$lala",1,1.2,true,null,[],["hi",["~#char","a"]]]]
    ["~keyword", "~lala", 1, 1.2, true, null, [], ["hi", "a"]]

.. note::

    to json conversions are lossy, this means that in order to not crash
    when serializing keywords, symbols and chars we do a lossy serialization,
    chars are strings, keywords are strings starting with : and symbols are
    strings starting with ~.

    The idea of this translation is to provide a way to view the edn or transit
    as json and shouldn't be used to send this data to a production system.

HTTP Requests
.............

You an make an http request that supports transit, json or edn but writting and
reading the request and response in a more readable way, for example, make a
request writing edn that will be transformed to transit before being sent, the
response will be transformed to edn if possible to make it more readable::

    $ echo '(increment {:value 20})' | transito http post http://localhost:8080/action e2t -

    Status: 200
    Content-Type: application/transit+json
    Content-Length: 28

    {:value [:count]}

You may ask, isn't it complected? yes, yes it is.

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
