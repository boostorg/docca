import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import argparse
import jinja2
from typing import List
from docca import (
    AcceptOneorNone,
    open_input,
    collect_compound_refs,
    collect_data,
    load_configs,
    construct_environment,
    Class,
    Namespace,
    Access,
    Compound,
    OverloadSet,
    TypeAlias,
    Enum,
    Variable,
    Entity,
    Type,
    FunctionKind
)

DEFAULT_TPLT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'include/docca/asciidoc'))

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

def render(env: jinja2.Environment, template_file: str, output_dir: str, output_file: str, **kwargs):
    output_path = os.path.join(output_dir, output_file)
    template = env.get_template(template_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wt', encoding='utf-8') as f:
        template.stream(**kwargs).dump(f)


def render_entities(env: jinja2.Environment, template_file: str, output_dir: str, entities):
    for e in entities:
        print(f'Rendering {e}')
        render(env, template_file, output_dir, asciidoc_file(e), entity=e)


def _sanitize_path_segment(s: str) -> str:
    return s.replace("[", "-lb") \
            .replace("]", "-rb")\
            .replace("(", "-lp")\
            .replace(")", "-rp")\
            .replace("<=>", "-spshp")\
            .replace("->", "-arrow")\
            .replace("operator>", "operator-gt")\
            .replace("operator~", "operator-bnot")\
            .replace("=", "-eq")\
            .replace("!", "-not")\
            .replace("+", "-plus")\
            .replace("&", "-and")\
            .replace("|", "-or")\
            .replace("^", "-xor")\
            .replace("*", "-star")\
            .replace("/", "-slash")\
            .replace("%", "-mod")\
            .replace("<", "-lt")\
            .replace(">", "-gt")\
            .replace("~", "dtor-")\
            .replace(",", "-comma")\
            .replace(":", "-")\
            .replace(" ", "-")


def asciidoc_file(e: Entity) -> str:
    file_path = '/'.join(_sanitize_path_segment(elm.name) for elm in e.path)
    return f'{file_path}.adoc'


def main():
    args = parse_args(sys.argv)

    file, ctx, data_dir = open_input(sys.stdin, args, os.getcwd())
    with ctx:
        refs = list(collect_compound_refs(file))
    data = collect_data(data_dir, refs)

    output_dir: str = args.output

    config = load_configs(args)

    env = construct_environment(
        jinja2.FileSystemLoader(DEFAULT_TPLT_DIR), config)
    env.filters['adocfile'] = asciidoc_file

    # Namespaces (not rendered directly)
    namespaces = [e for e in data.values() if isinstance(e, Namespace)]

    # Classes (including member types)
    classes = [e for e in data.values()
               if isinstance(e, Class) and e.access == Access.public and
                    not e.is_specialization]
    render_entities(env, 'class.jinja2', output_dir, classes)

    # Functions
    fns = []
    for e in [e2 for e2 in data.values() if isinstance(e2, Compound)]:
        fns += [mem for mem in e.members.values() if isinstance(mem, OverloadSet) and mem.access == Access.public]
    render_entities(env, 'overload-set.jinja2', output_dir, fns)
    
    # Type aliases
    type_alias = [e for e in data.values() if isinstance(e, TypeAlias)]
    render_entities(env, 'type-alias.jinja2', output_dir, type_alias)
    
    # Enums
    enums = [e for e in data.values() if isinstance(e, Enum)]
    render_entities(env, 'enum.jinja2', output_dir, enums)

    # Constants
    constants = []
    for ns in namespaces:
        constants += [e for e in ns.members.values() if isinstance(e, Variable)]
    render_entities(env, 'variable.jinja2', output_dir, constants)
    
    # Quickref
    render(
        env,
        'quickref.jinja2',
        output_dir,
        'reference.adoc',
        classes=classes,
        enums=enums,
        free_functions=[e for e in fns if isinstance(e.scope, Namespace)],
        type_aliases=[e for e in type_alias if isinstance(e.scope, Namespace)],
        constants=constants
    )



if __name__ == '__main__':
    main()