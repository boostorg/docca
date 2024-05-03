#!/usr/bin/env python

import argparse
import contextlib
import jinja2
import json
import io
import os.path
import sys
import xml.etree.ElementTree as ET


class Access:
    public = 'public'
    protected = 'protected'
    private = 'private'

class FunctionKind:
    static = 'static'
    nonstatic = 'nonstatic'
    friend = 'friend'
    free = 'free'

class VirtualKind:
    nonvirtual = 'non-virtual'
    purevirtual = 'pure-virtual'
    virtual = 'virtual'


class Linebreak():
    pass

class PhraseContainer:
    def __init__(self, parts):
        self._parts = parts

    def __getitem__(self, pos):
        return self._parts[pos]

    def __setitem__(self, pos, val):
        self._parts[pos] = val

    def __len__(self):
        return len(self._parts)

class Phrase(PhraseContainer):
    @property
    def text(self):
        return ''.join((
            part if isinstance(part, str)
                else '' if isinstance(part, Linebreak)
                else part.text
            for part in self
        ))

class Emphasised(Phrase):
    pass

class Monospaced(Phrase):
    pass

class Strong(Phrase):
    pass

class EntityRef(Phrase):
    def __init__(self, entity, parts):
        super().__init__(parts)
        self.entity = entity

    @property
    def text(self):
        result = super().text
        if not result:
            result = self.entity.fully_qualified_name
        return result

class UrlLink(Phrase):
    def __init__(self, url, parts):
        super().__init__(parts)
        self.url = url

    @property
    def text(self):
        result = super().text
        if not result:
            result = self.url
        return result


class Block:
    pass

class Paragraph(PhraseContainer, Block):
    def __init__(self, parts):
        super().__init__(parts)

    def __getitem__(self, pos):
        return self._parts[pos]

    def __len__(self):
        return len(self._parts)

class List(Block):
    def __init__(self, is_ordered, items):
        self.is_ordered = is_ordered
        self._items = items

    def __getitem__(self, pos):
        return self._items[pos]

    def __len__(self):
        return len(self._items)

class ListItem(Block):
    def __init__(self, blocks):
        self._blocks = blocks

    def __getitem__(self, pos):
        return self._items[pos]

    def __len__(self):
        return len(self._items)

class Section(Block):
    See = 'see'
    Returns = 'return'
    Author = 'author'
    Authors = 'authors'
    Version = 'version'
    Since = 'since'
    Date = 'date'
    Note = 'note'
    Warning = 'warning'
    Preconditions = 'pre'
    Postconditions = 'post'
    Copyright = 'copyright'
    Invariants = 'invariant'
    Remarks = 'remark'
    Attention = 'attention'
    Custom = 'par'
    RCS = 'rcs'

    def __init__(self, kind, title, blocks):
        self.kind = kind
        self.title = title
        self._blocks = blocks

    def __getitem__(self, pos):
        return self._blocks[pos]

    def __len__(self):
        return len(self._blocks)

class ParameterList(Block):
    parameters = 'param'
    return_values = 'retval'
    exceptions = 'exception'
    template_parameters = 'templateparam'

    def __init__(self, kind, items):
        self.kind = kind
        self._items = items

    def __getitem__(self, pos):
        return self._items[pos]

    def __len__(self):
        return len(self._items)

class ParameterDescription(Block):
    def __init__(self, description, params):
        self.description = description
        self._params = params

    def __getitem__(self, pos):
        return self._params[pos]

    def __len__(self):
        return len(self._params)

class ParameterItem(Block):
    def __init__(self, type, name, direction):
        self.type = type
        self.name = name
        self.direction = direction

    @property
    def is_in(self):
        return self.direction in ('in', 'inout')

    @property
    def is_out(self):
        return self.direction in ('out', 'inout')

class CodeBlock(Block):
    def __init__(self, lines):
        self._lines = lines

    def __getitem__(self, pos):
        return self._lines[pos]

    def __len__(self):
        return len(self._lines)


class Entity():
    access = Access.public
    _table = {
        ord('\r'): None,
        ord('\n'): None,
    }

    def __init__(self, element, scope, index):
        self.id = element.get('id')
        assert self.id

        self.brief = element.find('briefdescription')
        self.description = element.find('detaileddescription')
        self.scope = scope

        self.name = ''.join( element.find(self.nametag).itertext() )
        assert self.name

        self.groups = []

        loc = element.find('location')
        self._header = loc.get('file') if (loc is not None) else None

        self.index = index
        index[self.id] = self

    @property
    def header(self):
        return (
            self._header
            or (self.scope.header if self.scope else None)
        )

    @property
    def fully_qualified_name(self):
        return '::'.join((c.name for c in self.path))

    @property
    def path(self):
        result = self.scope.path if self.scope else []
        result.append(self)
        return result

    def resolve_references(self):
        self.brief = self.resolve_description(self.brief)
        self.description = self.resolve_description(self.description)

    def resolve_description(self, element):
        return self._block(element)

    def text_with_refs(self, elem):
        if elem is None:
            parts = []
        else:
            parts = self._phrase_content(elem, allow_missing_refs=True)
        return Phrase(parts)

    def entity_reference(self, element, allow_missing_refs=False):
        refid = element.get('refid')
        assert refid

        entity = self.index.get(refid)
        if entity:
            return EntityRef(
                entity,
                self._phrase_content(
                    element, allow_missing_refs=allow_missing_refs))

        if allow_missing_refs:
            Phrase(self._phrase_content(element, allow_missing_refs=True))


    def __lt__(self, other):
        return self.name < other.name

    def _block(self, element):
        result = []
        cur_para = []

        def finish_paragraph(cur_para):
            if cur_para:
                if isinstance(cur_para[0], str):
                    cur_para[0] = cur_para[0].lstrip()
                    if not cur_para[0]:
                        cur_para = cur_para[1:]
            if cur_para:
                if isinstance(cur_para[-1], str):
                    cur_para[-1] = cur_para[-1].rstrip()
                    if not cur_para[-1]:
                        cur_para = cur_para[:-1]

            # spaces after linebreaks usually cause issues
            for n in range(1, len(cur_para)):
                if (isinstance(cur_para[n - 1], Linebreak)
                        and isinstance(cur_para[n], str)):
                    cur_para[n] = cur_para[n].lstrip()

            if cur_para:
                result.append(Paragraph(cur_para))

            return []

        if element.text:
            cur_para.append(self._remove_endlines(element.text))

        for child in element:
            func = {
                'itemizedlist': self._list,
                'simplesect': self._section,
                'programlisting': self._codeblock,
                'parameterlist': self._parameters,
            }.get(child.tag)
            if func:
                cur_para = finish_paragraph(cur_para)
                result.append(func(child))
            elif child.tag == 'para':
                cur_para = finish_paragraph(cur_para)
                result.extend(self._block(child))
            else:
                cur_para.append(self._phrase(child))
            if child.tail:
                cur_para.append(self._remove_endlines(child.tail))

        finish_paragraph(cur_para)
        return result

    def _list(self, element):
        items = []
        for child in element:
            assert child.tag == 'listitem'
            items.append(self._block(child))
        return List(element.get('type') is not None, items)

    def _parameters(self, element):
        result = []
        descr = None
        kind = element.get('kind')
        for descr_block in element:
            assert descr_block.tag == 'parameteritem'
            descr = None
            params = []
            for item in descr_block:
                if item.tag == 'parameterdescription':
                    assert descr == None
                    descr = item
                    continue

                assert item.tag == 'parameternamelist'

                name = item.find('parametername')
                direction = name.get('direction') if name is not None else None
                params.append(
                    ParameterItem(
                        self.text_with_refs(item.find('parametertype')),
                        self.text_with_refs(name),
                        direction))

            assert descr
            result.append(ParameterDescription(self._block(descr), params))
        return ParameterList(kind, result)

    def _section(self, element):
        title = None
        if element and element[0].tag == 'title':
            title = self._phrase_content(element[0])
        title = Paragraph(title or [])

        kind = element.get('kind')

        parts = []
        for child in element:
            if child.tag == 'para':
                parts.extend(self._block(child))

        return Section(kind, title, parts)

    def _codeblock(self, element):
        lines = []
        for line in element:
            assert line.tag == 'codeline'
            text = ''
            for hl in line:
                assert hl.tag == 'highlight'
                if hl.text:
                    text += hl.text

                for part in hl:
                    if part.tag == 'sp':
                        text += ' '
                    elif part.tag == 'ref':
                        text += part.text or ''
                    if part.tail:
                        text += part.tail
                if hl.tail:
                    text += hl.tail
            lines.append(text)

        return CodeBlock(lines)


    def _phrase(self, element, allow_missing_refs=False):
        func = {
            'bold': self._strong,
            'computeroutput': self._monospaced,
            'emphasis': self._emphasised,
            'ref': self.entity_reference,
            'ulink': self._url_link,
            'linebreak': self._linebreak,
        }[element.tag]
        return func(element, allow_missing_refs=allow_missing_refs)

    def _phrase_content(self, element, allow_missing_refs=False):
        result = []
        if element.text:
            result.append(self._remove_endlines(element.text))

        for child in element:
            result.append(
                self._phrase(child, allow_missing_refs=allow_missing_refs))
            if child.tail:
                result.append(self._remove_endlines(child.tail))

        return result

    def _remove_endlines(self, s):
        return s.translate(self._table)

    def _strong(self, element, allow_missing_refs=False):
        return Strong(
            self._phrase_content(
                element, allow_missing_refs=allow_missing_refs))

    def _monospaced(self, element, allow_missing_refs=False):
        return Monospaced(
            self._phrase_content(
                element, allow_missing_refs=allow_missing_refs))

    def _emphasised(self, element, allow_missing_refs=False):
        return Emphasised(
            self._phrase_content(
                element, allow_missing_refs=allow_missing_refs))

    def _url_link(self, element, allow_missing_refs=False):
        url = element.get('url')
        assert url

        return UrlLink(
            url,
            self._phrase_content(
                element, allow_missing_refs=allow_missing_refs))

    def _linebreak(self, element, allow_missing_refs=None):
        return Linebreak()


class Compound(Entity):
    nametag = 'compoundname'

    def __init__(self, element, scope, index):
        super().__init__(element, scope, index)

        self.members={}

        self._nested = []
        for section in element:
            if section.tag in ('innerclass', 'innernamespace', 'innergroup'):
                self._nested.append((
                    section.get('prot', Access.public),
                    section.get('refid')))

    def adopt(self, entity, access):
        entity.scope = self
        entity.access = access

        assert entity.name not in self.members
        self.members[entity.name] = entity

    def resolve_references(self):
        super().resolve_references()

        for access, refid in self._nested:
            self.adopt(self.index[refid], access)
        delattr(self, '_nested')


class Member(Entity):
    nametag = 'name'

    def __init__(self, element, scope, index):
        super().__init__(element, scope, index)
        self.access = element.get('prot') or Access.public


class Group(Compound):
    nametag = 'title'

    def adopt(self, entity, access):
        entity.groups.append(self)


class Templatable(Entity):
    def __init__(self, element, scope, index):
        super().__init__(element, scope, index)

        tmp_elem = element.find('templateparamlist')
        self.template_parameters = [
            Parameter(tparam, self)
            for tparam in (tmp_elem or [])
        ]

        self.is_specialization = (
            (self.name.find('<') > 0) and (self.name.find('>') > 0))

    def resolve_references(self):
        super().resolve_references()

        for tparam in self.template_parameters:
            tparam.type = self.text_with_refs(tparam.type)
            tparam.default_value = self.text_with_refs(tparam.default_value)

            tparam.array = self.text_with_refs(tparam.array)
            if tparam.array:
                assert isinstance(tparam.type[-1], str)
                assert tparam.type[-1].endswith('(&)')
                tparam.type[-1] = tparam.type[-1][:-3]


class Type(Templatable):
    declarator = None
    objects = []


class Scope(Entity):
    def __init__(self, element, scope, index):
        super().__init__(element, scope, index)

        self.name = self.name.split('::')[-1]

        self.members = dict()
        self._friends = []
        for section in element:
            if not section.tag == 'sectiondef':
                continue

            for member_def in section:
                assert member_def.tag == 'memberdef'

                kind = member_def.get('kind')
                if (kind == 'friend'
                    and member_def.find('type').text == 'class'):
                    # ignore friend classes
                    continue

                factory = {
                    'function': OverloadSet.create,
                    'friend': OverloadSet.create,
                    'variable': Variable,
                    'typedef': TypeAlias,
                    'enum': Enum,
                }[kind]
                member = factory(member_def, section, self, index)
                if type(member) is OverloadSet:
                    key = (member.name, member.access, member.kind)
                    self.members[key] = member
                else:
                    assert member.name not in self.members
                    self.members[member.name] = member

    def resolve_references(self):
        super().resolve_references()


class Namespace(Scope, Compound):
    declarator = 'namespace'

    def resolve_references(self):
        super().resolve_references()

        for member in self.members.values():
            if isinstance(member, OverloadSet):
                for func in member:
                    func.is_free = True


class Class(Scope, Type, Compound):
    declarator = 'class'

    def __init__(self, element, scope, index):
        super().__init__(element, scope, index)
        self._bases = element.findall('basecompoundref')

    def resolve_references(self):
        super().resolve_references()

        self.bases = [
            Generalization(entry, self) for entry in  self._bases]
        delattr(self, '_bases')


class Generalization():
    def __init__(self, element, derived):
        self.is_virtual = element.get('virt') == 'virtual'
        self.access = element.get('prot')
        assert self.access

        if element.get('refid'):
            self.base = derived.entity_reference(element)
        else:
            self.base = derived.text_with_refs(element)


class Struct(Class):
    declarator = 'struct'


class Union(Class):
    declarator = 'union'


class Enum(Scope, Type, Member):
    def __init__(self, element, section, parent, index):
        super().__init__(element, parent, index)
        self.is_scoped = element.get('strong') == 'yes'
        self.underlying_type = element.find('type')

        self.objects = []
        for child in element.findall('enumvalue'):
            enumerator = Enumerator(child, section, self, index)
            self.objects.append(enumerator)
            enumerator.scope.members[enumerator.name] = enumerator

    @property
    def declarator(self):
        return 'enum class' if self.is_scoped else 'enum'

    def resolve_references(self):
        super().resolve_references()
        self.underlying_type = self.text_with_refs(self.underlying_type)


class Value(Member, Templatable):
    def __init__(self, element, parent, index):
        super().__init__(element, parent, index)
        self.is_static = element.get('static') == 'yes'
        self.is_constexpr = element.get('constexpr') == 'yes'
        self.is_volatile = element.get('volatile') == 'yes'
        self.is_const = (
            element.get('const') == 'yes'
            or element.get('mutable') == 'no'
            or False)
        self.is_inline = element.get('inline') == 'yes'


class Function(Value):
    def __init__(self, element, section, parent, index):
        super().__init__(element, parent, index)
        self.is_explicit = element.get('explicit') == 'yes'
        self.refqual = element.get('refqual')
        self.virtual_kind = element.get('virt', VirtualKind.nonvirtual)
        self.is_friend = section.get('kind') == 'friend'
        self.is_free = section.get('kind') == 'related'
        self.is_constructor = self.name == parent.name
        self.is_destructor = self.name == '~' + parent.name
        self.is_noexcept = (
            element.get('noexcept') == 'yes' or self.is_destructor)

        args = element.find('argsstring').text or ''
        self.is_deleted = args.endswith('=delete')
        self.is_defaulted = args.endswith('=default')

        self.overload_set = None

        self.return_type = element.find('type')
        assert self.return_type is not None

        self.parameters = [
            Parameter(param, self)
            for param in element.findall('param')
        ]

    @property
    def kind(self):
        if self.is_friend:
            return FunctionKind.friend
        if self.is_free:
            return FunctionKind.free
        if self.is_static:
            return FunctionKind.static
        return FunctionKind.nonstatic

    @property
    def is_sole_overload(self):
        return len(self.overload_set) == 1

    @property
    def overload_index(self):
        if self.overload_set is None or self.is_sole_overload:
            return -1

        for n, overload in enumerate(self.overload_set):
            if self == overload:
                return n

        return -1

    def resolve_references(self):
        super().resolve_references()

        self.return_type = self.text_with_refs(self.return_type)
        for param in self.parameters:
            param.default_value = self.text_with_refs(param.default_value)
            param.type = self.text_with_refs(param.type)

            param.array = self.text_with_refs(param.array)
            if param.array:
                assert isinstance(param.type[-1], str)
                assert param.type[-1].endswith('(&)')
                param.type[-1] = param.type[-1][:-3]

    def __lt__(self, other):
        if not isinstance(other, Function):
            return self.name < other.name

        if self.name == other.name:
            if self.scope == parent.scope:
                return self.overload_index < other.overload_index
            return self.scope < other.scope

        # if self.is_constructor:
        #     return True
        # if other.is_constructor:
        #     return False
        # if self.is_destructor:
        #     return True
        # if other.is_destructor:
        #     return False
        return self.name < other.name


class Parameter():
    def __init__(self, element, parent):
        self.type = element.find('type')
        self.default_value = element.find('defval')
        self.description = element.find('briefdescription')
        self.array = element.find('array')
        self.name = element.find('declname')
        if self.name is not None:
            self.name = self.name.text


class OverloadSet():
    @staticmethod
    def create(element, section, parent, index):
        func = Function(element, section, parent, index)

        key = (func.name, func.access, func.kind)
        if key in parent.members:
            overload_set = parent.members[key]
            overload_set.append(func)
        else:
            overload_set = OverloadSet([func])
        func.overload_set = overload_set
        return overload_set

    def __init__(self, funcs):
        self.funcs = funcs
        assert len(funcs)
        self._resort()

    def append(self, func):
        self.funcs.append(func)
        self._resort()

    def __getattr__(self, name):
        return getattr(self.funcs[0], name)

    @property
    def brief(self):
        return [func.brief for func in self.funcs]

    def __getitem__(self, pos):
        return self.funcs[pos]

    def __len__(self):
        return len(self.funcs)

    def __lt__(self, other):
        if isinstance(other, OverloadSet):
            return self.funcs[0] < other.funcs[0]
        return self.name < other.name

    def _resort(self):
        funcs_backwards = []
        briefs_backwards = []
        for func in self.funcs:
            brief = ''.join(func.brief.itertext())
            try:
                n = briefs_backwards.index(brief)
            except:
                n = 0
            briefs_backwards.insert(n, brief)
            funcs_backwards.insert(n, func)
        funcs_backwards.reverse()
        self.funcs = funcs_backwards


class Variable(Value):
    def __init__(self, element, section, parent, index):
        super().__init__(element, parent, index)

        self.value = element.find('initializer')
        self.type = element.find('type')

    def resolve_references(self):
        super().resolve_references()
        self.value = self.text_with_refs(self.value)
        self.type = self.text_with_refs(self.type)


class Enumerator(Variable):
    def __init__(self, element, section, parent, index):
        super().__init__(element, section, parent, index)
        self.is_constexpr = True
        self.is_const = True
        self.is_static = True

        self._enum = parent
        self.scope = parent if parent.is_scoped else parent.scope

    def resolve_references(self):
        super().resolve_references()

        self.type = Phrase([EntityRef(self._enum, [self._enum.name])])
        delattr(self, '_enum')


class TypeAlias(Member, Type):
    declarator = 'using'

    def __init__(self, element, section, parent, index):
        super().__init__(element, parent, index)

        self.aliased = element.find('type')
        assert self.aliased is not None

    def resolve_references(self):
        super().resolve_references()
        self.aliased = self.text_with_refs(self.aliased)


class Friend(Member):
    def __init__(self, element, section, parent, index):
        super().__init__(element, parent, index)


class AcceptOneorNone(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        if kwargs.get('nargs') is not None:
            raise ValueError("nargs not allowed")
        if kwargs.get('const') is not None:
            raise ValueError("const not allowed")
        if kwargs.get('default') is not None:
            raise ValueError("default not allowed")

        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest) is not None:
            raise argparse.ArgumentError(self, "multiple values")

        setattr(namespace, self.dest, values)

def parse_args(args):
    parser = argparse.ArgumentParser(
        prog=args[0],
        description='Produces API reference in QuickBook markup')
    parser.add_argument(
        '-i',
        '--input',
        action=AcceptOneorNone,
        help='Doxygen XML index file; STDIN by default')
    parser.add_argument(
        '-o',
        '--output',
        action=AcceptOneorNone,
        help='Output file; STDOUT by default')
    parser.add_argument(
        '-c', '--config',
        action='append',
        default=[],
        help='Configuration files')
    parser.add_argument(
        '-T', '--template',
        action=AcceptOneorNone,
        help='Jinja2 template to use for output')
    parser.add_argument(
        '-I', '--include',
        action='append',
        default=[],
        help='Directory with template partials')
    parser.add_argument(
        '-D', '--directory',
        action=AcceptOneorNone,
        help=(
            'Directory with additional data files; '
            'by default INPUT parent directory if that is provided, '
            'otherwise PWD'))
    return parser.parse_args(args[1:])

def get_config(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def collect_compound_refs(file):
    tree = ET.parse(file)
    root = tree.getroot()
    for child in root:
        if child.tag != 'compound':
            continue

        kind = child.get('kind')
        assert kind
        if kind in ('file', 'dir'):
            continue

        refid = child.get('refid')
        assert refid
        yield refid

def collect_data(parent_dir, refs):
    result = dict()
    for refid in refs:
        file_name = os.path.join(parent_dir, refid) + '.xml'
        with open(file_name, 'r') as file:
            tree = ET.parse(file)
            root = tree.getroot()
            assert len(root) == 1

            element = root[0]
            assert element.tag == 'compounddef'

            factory = {
                'class': Class,
                'namespace': Namespace,
                'struct': Struct,
                'union': Union,
                'group': Group
            }.get(element.get('kind'))
            if not factory:
                continue
            factory(element, None, result)

    for entity in result.values():
        assert entity is not None
        entity.resolve_references();

    return result

def construct_environment(includes, config):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(includes),
        autoescape=False,
        undefined=jinja2.StrictUndefined,
        extensions=[
            'jinja2.ext.do',
            'jinja2.ext.loopcontrols',
        ],
    )

    env.globals['Access'] = Access
    env.globals['FunctionKind'] = FunctionKind
    env.globals['VirtualKind'] = VirtualKind
    env.globals['Section'] = Section
    env.globals['ParameterList'] = ParameterList
    env.globals['Config'] = config

    env.tests['Entity'] = lambda x: isinstance(x, Entity)
    env.tests['Templatable'] = lambda x: isinstance(x, Templatable)
    env.tests['Type'] = lambda x: isinstance(x, Type)
    env.tests['Scope'] = lambda x: isinstance(x, Scope)
    env.tests['Namespace'] = lambda x: isinstance(x, Namespace)
    env.tests['TypeAlias'] = lambda x: isinstance(x, TypeAlias)
    env.tests['Class'] = lambda x: isinstance(x, Class)
    env.tests['Struct'] = lambda x: isinstance(x, Struct)
    env.tests['Union'] = lambda x: isinstance(x, Union)
    env.tests['Enum'] = lambda x: isinstance(x, Enum)
    env.tests['Value'] = lambda x: isinstance(x, Value)
    env.tests['Variable'] = lambda x: isinstance(x, Variable)
    env.tests['Function'] = lambda x: isinstance(x, Function)
    env.tests['OverloadSet'] = lambda x: isinstance(x, OverloadSet)
    env.tests['Parameter'] = lambda x: isinstance(x, OverloadSet)

    env.tests['Phrase'] = lambda x: isinstance(x, Phrase)
    env.tests['Linebreak'] = lambda x: isinstance(x, Linebreak)
    env.tests['Emphasised'] = lambda x: isinstance(x, Emphasised)
    env.tests['Strong'] = lambda x: isinstance(x, Strong)
    env.tests['Monospaced'] = lambda x: isinstance(x, Monospaced)
    env.tests['EntityRef'] = lambda x: isinstance(x, EntityRef)
    env.tests['UrlLink'] = lambda x: isinstance(x, UrlLink)

    env.tests['Block'] = lambda x: isinstance(x, Block)
    env.tests['Paragraph'] = lambda x: isinstance(x, Paragraph)
    env.tests['List'] = lambda x: isinstance(x, List)
    env.tests['ListItem'] = lambda x: isinstance(x, ListItem)
    env.tests['Section'] = lambda x: isinstance(x, Section)
    env.tests['CodeBlock'] = lambda x: isinstance(x, CodeBlock)
    env.tests['ParameterList'] = lambda x: isinstance(x, ParameterList)
    env.tests['ParameterDescription'] = lambda x: isinstance(x, ParameterDescription)
    env.tests['ParameterItem'] = lambda x: isinstance(x, ParameterItem)

    return env

def main(args, stdin, stdout, includes):
    args = parse_args(args)

    data_dir = args.directory

    if args.input:
        file = open(args.input, 'r')
        ctx = file
        data_dir = data_dir or os.path.dirname(args.input)
    else:
        file = stdin
        ctx = contextlib.nullcontext()
        data_dir = data_dir or os.getcwd()
    with ctx:
        refs = list(collect_compound_refs(file))
    data = collect_data(data_dir, refs)

    config = {
        'include_private': False,
        'legacy_behavior': True,
    }
    for file_name in args.config:
        config.update(get_config(file_name))

    if args.output:
        file = open(args.output, 'w')
        ctx = file
    else:
        file = stdout
        ctx = contextlib.nullcontext()
    with ctx:
        template_file = (args.template
             or os.path.join(includes, 'docca/quickbook.jinja2'))

        env = construct_environment(
            [os.path.dirname(template_file), includes] + args.include,
            config)

        template = env.get_template(os.path.basename(template_file))
        template.stream(entities=data).dump(file)

if __name__ == '__main__':
    includes = os.path.dirname(os.path.realpath(__file__))
    includes = os.path.join(includes, 'include')
    main(sys.argv, sys.stdin, sys.stdout, includes)
