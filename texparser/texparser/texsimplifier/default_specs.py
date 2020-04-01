# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>


import unicodedata
import datetime
import sys

if sys.version_info.major >= 3:
    def unicode(string): return string
    basestring = str
else:
    pass



from texparser.texsimplifier import MacroTextSpec, EnvironmentTextSpec, SpecialsTextSpec, \
    fmt_equation_environment, fmt_placeholder_node, placeholder_node_formatter, fmt_input_macro, \
    fmt_reconstruct_macro, fmt_replace_documentclass, fmt_verb_macro, fmt_replace_begin_document



def _format_uebung(n, l2t):
    s = '\n' + l2t.nodelist_to_simplified([n.nodeargs[0]]) + '\n'
    optarg = n.nodeargs[1]
    if optarg is not None:
        s += '[{}]\n'.format(l2t.nodelist_to_simplified([optarg]))
    return s

def _format_maketitle(l2tobj, title, author, date):
    if title == None:
        pass
        setattr(l2tobj, "__replace_maketitle", True)
        return ""
    else:
        s = title + '\n'
        s += '    ' + author + '\n'
        s += '    ' + date + '\n'
        s += '='*max(len(title), 4+len(author), 4+len(date)) + '\n\n'
        return s

def _latex_today():
    return '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())


# construct the specs structure, more than the just the following definition

latex_base_specs = {
    
    'environments': [

        # Dirty hack: some documents don't have a \maketitle so let's hardcode it right after begin{document}
        EnvironmentTextSpec('document', simplify_repl="\n\\tolerance=1\n\\emergencystretch=\\maxdimen\n\\hyphenpenalty=10000\n\\hbadness=10000\n\\begin{document}\n\\lsstyle\n\\fontdimen2\\font=0.6ex\n%s\n\\end{document}"), # \n\\newpage...\n\\maketitle
        # simplify_repl=fmt_replace_begin_document), 
        EnvironmentTextSpec('equation', simplify_repl="[MATH]"),
        EnvironmentTextSpec('equation*', simplify_repl="[MATH]"),
        EnvironmentTextSpec('eqnarray', simplify_repl="[MATH]"),
        EnvironmentTextSpec('align', simplify_repl="[MATH]"),
        EnvironmentTextSpec('multline', simplify_repl=fmt_equation_environment),
        EnvironmentTextSpec('gather', simplify_repl=fmt_equation_environment),
        EnvironmentTextSpec('dmath', simplify_repl="[MATH]"),

        EnvironmentTextSpec('array', simplify_repl="[MATH]"),
        EnvironmentTextSpec('pmatrix', simplify_repl="[MATH]"),
        EnvironmentTextSpec('bmatrix', simplify_repl="[MATH]"),
        EnvironmentTextSpec('smallmatrix', simplify_repl="[MATH]"),

        EnvironmentTextSpec('center', simplify_repl='\n%s\n'),
        EnvironmentTextSpec('flushleft', simplify_repl='\n%s\n'),
        EnvironmentTextSpec('flushright', simplify_repl='\n%s\n'),

        EnvironmentTextSpec('exenumerate', discard=False),
        EnvironmentTextSpec('enumerate', discard=False),
        EnvironmentTextSpec('list', discard=False),
        EnvironmentTextSpec('itemize', discard=False),
        EnvironmentTextSpec('subequations', discard=True),
        EnvironmentTextSpec('figure', discard=True),
        EnvironmentTextSpec('table', discard=True),
        EnvironmentTextSpec('tabular', discard=True),
        EnvironmentTextSpec('tabular*', discard=True),
        EnvironmentTextSpec('minipage', discard=True),

        EnvironmentTextSpec('abstract', discard=False),
        
        EnvironmentTextSpec('quote', discard=False),

    ],
    'specials': [
        SpecialsTextSpec('&', '   '), # ignore tabular alignments, just add a little space
    ],

    'macros': [
        # NOTE: macro will only be assigned arguments if they are explicitly defined as
        #       accepting arguments in latexwalker.py.
        MacroTextSpec('documentclass', simplify_repl=fmt_replace_documentclass),
        MacroTextSpec('geometry', discard=True),
        MacroTextSpec('usepackage', discard=False),
        MacroTextSpec('emph', discard=False),
        MacroTextSpec('textrm', discard=False),
        MacroTextSpec('textit', discard=False),
        MacroTextSpec('textbf', discard=False),
        MacroTextSpec('textsc', discard=False),
        MacroTextSpec('textsl', discard=False),
        MacroTextSpec('text', discard=False),
        MacroTextSpec('lsstyle', discard=False),
        MacroTextSpec('textquoteleft', discard=False),
        MacroTextSpec('textquoteright', discard=False),
        MacroTextSpec('textquotedblright', discard=False),
        MacroTextSpec('textquotedblleft', discard=False),
        MacroTextSpec('textpm', discard=False),
        MacroTextSpec('textmp', discard=False),
        MacroTextSpec('texteuro', discard=False),
        MacroTextSpec('backslash', discard=False),
        MacroTextSpec('textbackslash', discard=False),
        MacroTextSpec('textendash', discard=False),
        MacroTextSpec('textemdash', discard=False),
        MacroTextSpec('verb', simplify_repl=fmt_verb_macro),

        MacroTextSpec('mathrm', discard=False),
        MacroTextSpec('mathbb', discard=False),
        MacroTextSpec('mathbf', discard=False),
        MacroTextSpec('mathsf', discard=False),
        MacroTextSpec('mathscr', discard=False),
        MacroTextSpec('mathfrak', discard=False),


        MacroTextSpec('caption', discard=True),
        MacroTextSpec('affiliation', discard=True),
        MacroTextSpec('address', discard=True),
        MacroTextSpec('preprint', discard=True),
        MacroTextSpec('date', simplify_repl="\\date{}\n"),
        # We must include this hack here:
        # Remove the maketitle if there is any, we will hardcoded add it right after begin{document}!
        MacroTextSpec('author', discard=True),
        MacroTextSpec('shortauthors', discard=True),
        MacroTextSpec('title', discard=False),
        MacroTextSpec('maketitle', discard=False),

        MacroTextSpec('newtheorem', discard=True),
        MacroTextSpec('newtheorem*', discard=True),


        MacroTextSpec('hspace', discard=True),
        MacroTextSpec('vspace', discard=True),
        MacroTextSpec('hspace*', discard=True),
        MacroTextSpec('vspace*', discard=True),


        MacroTextSpec('input', simplify_repl=fmt_input_macro),
        MacroTextSpec('include', simplify_repl=fmt_input_macro),


        #
        # Math
        #
        MacroTextSpec('hbar', discard=True),
        MacroTextSpec('ell', discard=True),
        MacroTextSpec('forall', discard=True),
        MacroTextSpec('complement', discard=True),
        MacroTextSpec('partial', discard=True),
        MacroTextSpec('exists', discard=True),
        MacroTextSpec('nexists', discard=True),
        MacroTextSpec('varnothing', discard=True),
        MacroTextSpec('emptyset', discard=True),
        MacroTextSpec('aleph', discard=True),
        MacroTextSpec('nabla', discard=True),

        MacroTextSpec('in', discard=True),
        MacroTextSpec('notin', discard=True),
        MacroTextSpec('ni', discard=True),
        MacroTextSpec('prod', discard=True),
        MacroTextSpec('coprod', discard=True),
        MacroTextSpec('sum', discard=True),
        MacroTextSpec('setminus', discard=True),
        MacroTextSpec('smallsetminus', discard=True),
        MacroTextSpec('ast', discard=True),
        MacroTextSpec('circ', discard=True),
        MacroTextSpec('bullet', discard=True),
        MacroTextSpec('sqrt', discard=True),
        MacroTextSpec('propto', discard=True),
        MacroTextSpec('infty', discard=True),
        MacroTextSpec('parallel', discard=True),
        MacroTextSpec('nparallel', discard=True),
        MacroTextSpec('wedge', discard=True),
        MacroTextSpec('vee', discard=True),
        MacroTextSpec('cap', discard=True),
        MacroTextSpec('cup', discard=True),
        MacroTextSpec('int', discard=True),
        MacroTextSpec('iint', discard=True),
        MacroTextSpec('iiint', discard=True),
        MacroTextSpec('oint', discard=True),

        MacroTextSpec('sim', discard=True),
        MacroTextSpec('backsim', discard=True),
        MacroTextSpec('simeq', discard=True),
        MacroTextSpec('approx', discard=True),
        MacroTextSpec('neq', discard=True),
        MacroTextSpec('equiv', discard=True),
        MacroTextSpec('ge', discard=True),
        MacroTextSpec('le', discard=True),
        MacroTextSpec('leq', discard=True),
        MacroTextSpec('geq', discard=True),
        MacroTextSpec('leqslant', discard=True),
        MacroTextSpec('geqslant', discard=True),
        MacroTextSpec('leqq', discard=True),
        MacroTextSpec('geqq', discard=True),
        MacroTextSpec('ll', discard=True),
        MacroTextSpec('gg', discard=True),
        MacroTextSpec('nless', discard=True),
        MacroTextSpec('ngtr', discard=True),
        MacroTextSpec('nleq', discard=True),
        MacroTextSpec('ngeq', discard=True),
        MacroTextSpec('lesssim', discard=True),
        MacroTextSpec('lessgtr', discard=True),
        MacroTextSpec('gtrless', discard=True),
        MacroTextSpec('prec', discard=True),
        MacroTextSpec('succ', discard=True),
        MacroTextSpec('preceq', discard=True),
        MacroTextSpec('succeq', discard=True),
        MacroTextSpec('succsim', discard=True),
        MacroTextSpec('precsim', discard=True),
        MacroTextSpec('nprec', discard=True),
        MacroTextSpec('nsucc', discard=True),
        MacroTextSpec('subset', discard=True),
        MacroTextSpec('supset', discard=True),
        MacroTextSpec('subseteq', discard=True),
        MacroTextSpec('supseteq', discard=True),
        MacroTextSpec('nsubseteq', discard=True),
        MacroTextSpec('bsupseteq', discard=True),
        MacroTextSpec('subsetneq', discard=True),
        MacroTextSpec('supsetneq', discard=True),
        MacroTextSpec('hbar', discard=True),
        MacroTextSpec('hbar', discard=True),
        MacroTextSpec('hbar', discard=True),

        MacroTextSpec('cdot', discard=True),
        MacroTextSpec('times', discard=True),
        MacroTextSpec('otimes', discard=True),
        MacroTextSpec('oplus', discard=True),
        MacroTextSpec('bigotimes', discard=True),
        MacroTextSpec('bigoplus', discard=True),

        MacroTextSpec('frac', discard=True),
        MacroTextSpec('nicefrac', discard=True),

        MacroTextSpec('cos', discard=True),
        MacroTextSpec('sin', discard=True),
        MacroTextSpec('tan', discard=True),
        MacroTextSpec('arccos', discard=True),
        MacroTextSpec('arcsin', discard=True),
        MacroTextSpec('arctan', discard=True),
        MacroTextSpec('cosh', discard=True),
        MacroTextSpec('sinh', discard=True),
        MacroTextSpec('tanh', discard=True),
        MacroTextSpec('arccosh', discard=True),
        MacroTextSpec('arcsinh', discard=True),
        MacroTextSpec('arctanh', discard=True),

        MacroTextSpec('ln', discard=True),
        MacroTextSpec('log', discard=True),

        MacroTextSpec('max', discard=True),
        MacroTextSpec('min', discard=True),
        MacroTextSpec('sup', discard=True),
        MacroTextSpec('inf', discard=True),
        MacroTextSpec('lim', discard=True),
        MacroTextSpec('limsup', discard=True),
        MacroTextSpec('liminf', discard=True),

        MacroTextSpec('prime', discard=True),
        MacroTextSpec('dag', discard=True),
        MacroTextSpec('dagger', discard=True),
        MacroTextSpec('pm', discard=True),
        MacroTextSpec('mp', discard=True),
        MacroTextSpec('quad', discard=True),
        MacroTextSpec('qquad', discard=True),
        MacroTextSpec('ldots', discard=True),
        MacroTextSpec('cdots', discard=True),
        MacroTextSpec('ddots', discard=True),
        MacroTextSpec('dots', discard=True),

        MacroTextSpec('langle', discard=True),
        MacroTextSpec('rangle', discard=True),
        MacroTextSpec('lvert', discard=True),
        MacroTextSpec('rvert', discard=True),
        MacroTextSpec('lVert', discard=True),
        MacroTextSpec('rVert', discard=True),
        MacroTextSpec('Vert', discard=True),
        MacroTextSpec('mid', discard=True),
        MacroTextSpec('nmid', discard=True),
        MacroTextSpec('ket', discard=True),
        MacroTextSpec('bra', discard=True),
        MacroTextSpec('braket', discard=True),
        MacroTextSpec('ketbra', discard=True),
        MacroTextSpec('uparrow', discard=True),
        MacroTextSpec('downarrow', discard=True),
        MacroTextSpec('rightarrow', discard=True),
        MacroTextSpec('Downarrow', discard=True),
        MacroTextSpec('Rightarrow', discard=True),
        MacroTextSpec('to', discard=True),
        MacroTextSpec('leftarrow', discard=True),
        MacroTextSpec('rightarrow', discard=True),
        MacroTextSpec('Leftarrow', discard=True),
        MacroTextSpec('Rightarrow', discard=True),
        MacroTextSpec('longrightarrow', discard=True),
        MacroTextSpec('longleftarrow', discard=True),
        MacroTextSpec('id', discard=True),
        MacroTextSpec('Ident', discard=True),

    ] + [ MacroTextSpec(x, simplify_repl=y, discard=False, n=z) for x, y, z in (

        ('today', "", None),


        #('includegraphics', placeholder_node_formatter('graphics')),
        ('includegraphics', None, None),

        ('ref', '[REF]', None),
        ('autoref', '[REF]', None),
        ('cref', '[REF]', None),
        ('Cref', '[REF]', None),
        ('eqref', '([REF])', None),
        ('url', '<%s>', None),
        #('item',
        # lambda r, l2tobj: '\n  '+(
        #     l2tobj.nodelist_to_simplified([r.nodeoptarg]) if r.nodeoptarg else '* '
        # ), None
        #) ,
        #('footnote', '[%s]', None),
        ('href', lambda n, l2tobj:  \
         '{} <{}>'.format(l2tobj.nodelist_to_simplified([n.nodeargd.argnlist[1]]), 
                          l2tobj.nodelist_to_simplified([n.nodeargd.argnlist[0]])), None),

        ('cite', '[CIT.]', None),
        ('citet', '[CIT.]', None),
        ('citep', '[CIT.]', None),
        ('citeauthor', '[CIT.]', None),

        # use second argument:
        #('texorpdfstring', lambda node, l2t: l2t.nodelist_to_simplified(node.nodeargs[1:2])),


        ('part', None, None),
        ('chapter', None, None),
        ('section', None, None),
        ('subsection', None, None),
        ('subsubsection', None, None),
        ('paragraph', None, None),
        ('subparagraph', None, None),
        
        #('hspace', '', None),
        #('vspace', '\', None),

        #('oe', u'\u0153', None),
        #('OE', u'\u0152', None),
        #('ae', u'\u00e6', None),
        #('AE', u'\u00c6', None),
        #('aa', u'\u00e5', None), # a norvegien/nordique
        #('AA', u'\u00c5', None), # A norvegien/nordique
        #('o', u'\u00f8', None), # o norvegien/nordique
        #('O', u'\u00d8', None), # O norvegien/nordique
        #('ss', u'\u00df', None), # s-z allemand
        #('L', u"\N{LATIN CAPITAL LETTER L WITH STROKE}", None),
        #('l', u"\N{LATIN SMALL LETTER L WITH STROKE}", None),
        #('i', u"\N{LATIN SMALL LETTER DOTLESS I}", None),
        #('j', u"\N{LATIN SMALL LETTER DOTLESS J}", None),

        ("~", None, None),
        ("&", None, None),
        ("$", None, None),
        ("{", None, None),
        ("}", None, None),
        ("%", lambda arg: "\\%" , None), # careful: % is formatting substitution symbol...
        ("#", None, None),
        ("_", None, None),

        ("\\", None, None),
        ("\"", None, None),

    )]
}


specs = [
    #
    # CATEGORY: latex-base
    #
    ('latex-base', latex_base_specs),

    #
    # CATEGORY: nonascii-specials
    #
    ('nonascii-specials', {
        'macros': [],
        'environments': [],
        'specials': []
    }),
]
