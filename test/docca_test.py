#
# Copyright (c) 2024 Dmitry Arkhipov (grisumbras@yandex.ru)
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
# Official repository: https://github.com/boostorg/json
#

import docca

import jinja2
import jinja2.ext


def test_construct_environment():
    conf = dict()
    env = docca.construct_environment([], conf)

    assert not env.autoescape

    assert env.undefined == jinja2.StrictUndefined

    assert [
        ext for ext in env.extensions.values()
        if isinstance(ext, jinja2.ext.do)
    ]
    assert [
        ext for ext in env.extensions.values()
        if isinstance(ext, jinja2.ext.loopcontrols)
    ]

    assert env.globals['Access'] == docca.Access
    assert env.globals['FunctionKind'] == docca.FunctionKind
    assert env.globals['VirtualKind'] == docca.VirtualKind
    assert env.globals['Section'] == docca.Section
    assert env.globals['ParameterList'] == docca.ParameterList
    assert env.globals['Config'] == conf
