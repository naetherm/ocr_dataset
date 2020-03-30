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
        MacroTextSpec('verb', simplify_repl=fmt_verb_macro),

        MacroTextSpec('mathrm', discard=False),
        MacroTextSpec('mathbb', discard=False),
        MacroTextSpec('mathbf', discard=False),
        MacroTextSpec('mathsf', discard=False),
        MacroTextSpec('mathscr', discard=False),
        MacroTextSpec('mathfrak', discard=False),


        MacroTextSpec('caption', discard=True),
        MacroTextSpec('author', discard=True),
        MacroTextSpec('shortauthors', discard=True),
        MacroTextSpec('title', discard=False),
        MacroTextSpec('affiliation', discard=True),
        MacroTextSpec('address', discard=True),
        MacroTextSpec('preprint', discard=True),
        MacroTextSpec('date', simplify_repl="\\date{}\n"),
        # We must include this hack here:
        # Remove the maketitle if there is any, we will hardcoded add it right after begin{document}!
        MacroTextSpec('maketitle', discard=False),

        MacroTextSpec('newtheorem', discard=True),
        MacroTextSpec('newtheorem*', discard=True),


        MacroTextSpec('input', simplify_repl=fmt_input_macro),
        MacroTextSpec('include', simplify_repl=fmt_input_macro),

    ] + [ MacroTextSpec(x, simplify_repl=y, discard=False, n=z) for x, y, z in (

        ('today', None, None),


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
        
        ('hspace', '', None),
        ('vspace', '\n', None),

        ('oe', u'\u0153', None),
        ('OE', u'\u0152', None),
        ('ae', u'\u00e6', None),
        ('AE', u'\u00c6', None),
        ('aa', u'\u00e5', None), # a norvegien/nordique
        ('AA', u'\u00c5', None), # A norvegien/nordique
        ('o', u'\u00f8', None), # o norvegien/nordique
        ('O', u'\u00d8', None), # O norvegien/nordique
        ('ss', u'\u00df', None), # s-z allemand
        ('L', u"\N{LATIN CAPITAL LETTER L WITH STROKE}", None),
        ('l', u"\N{LATIN SMALL LETTER L WITH STROKE}", None),
        ('i', u"\N{LATIN SMALL LETTER DOTLESS I}", None),
        ('j', u"\N{LATIN SMALL LETTER DOTLESS J}", None),

        ("~", "~" , None),
        ("&", "&" , None),
        ("$", "$" , None),
        ("{", "{" , None),
        ("}", "}" , None),
        ("%", lambda arg: "%" , None), # careful: % is formatting substitution symbol...
        ("#", "#" , None),
        ("_", "_" , None),

        ("\\", '\n', None),

        ("textquoteleft", "\N{LEFT SINGLE QUOTATION MARK}", None),
        ("textquoteright", "\N{RIGHT SINGLE QUOTATION MARK}", None),
        ("textquotedblright", u"\N{RIGHT DOUBLE QUOTATION MARK}", None),
        ("textquotedblleft", u"\N{LEFT DOUBLE QUOTATION MARK}", None),
        ("textendash", u"\N{EN DASH}", None),
        ("textemdash", u"\N{EM DASH}", None),

        ('textpm', u"\N{PLUS-MINUS SIGN}", None),
        ('textmp', u"\N{MINUS-OR-PLUS SIGN}", None),

        ("texteuro", u"\N{EURO SIGN}", None),

        ("backslash", "\\", None),
        ("textbackslash", "\\", None),

        # math stuff

        ("hbar", u"\N{LATIN SMALL LETTER H WITH STROKE}", None),
        ("ell", u"\N{SCRIPT SMALL L}", None),

        ('forall', u"\N{FOR ALL}", None),
        ('complement', u"\N{COMPLEMENT}", None),
        ('partial', u"\N{PARTIAL DIFFERENTIAL}", None),
        ('exists', u"\N{THERE EXISTS}", None),
        ('nexists', u"\N{THERE DOES NOT EXIST}", None),
        ('varnothing', u"\N{EMPTY SET}", None),
        ('emptyset', u"\N{EMPTY SET}", None),
        ('aleph', u"\N{ALEF SYMBOL}", None),
        # increment?
        ('nabla', u"\N{NABLA}", None),
        #
        ('in', u"\N{ELEMENT OF}", None),
        ('notin', u"\N{NOT AN ELEMENT OF}", None),
        ('ni', u"\N{CONTAINS AS MEMBER}", None),
        ('prod', u'\N{N-ARY PRODUCT}', None),
        ('coprod', u'\N{N-ARY COPRODUCT}', None),
        ('sum', u'\N{N-ARY SUMMATION}', None),
        ('setminus', u'\N{SET MINUS}', None),
        ('smallsetminus', u'\N{SET MINUS}', None),
        ('ast', u'\N{ASTERISK OPERATOR}', None),
        ('circ', u'\N{RING OPERATOR}', None),
        ('bullet', u'\N{BULLET OPERATOR}', None),
        ('sqrt', u'\N{SQUARE ROOT}(%(2)s)', None),
        ('propto', u'\N{PROPORTIONAL TO}', None),
        ('infty', u'\N{INFINITY}', None),
        ('parallel', u'\N{PARALLEL TO}', None),
        ('nparallel', u'\N{NOT PARALLEL TO}', None),
        ('wedge', u"\N{LOGICAL AND}", None),
        ('vee', u"\N{LOGICAL OR}", None),
        ('cap', u'\N{INTERSECTION}', None),
        ('cup', u'\N{UNION}', None),
        ('int', u'\N{INTEGRAL}', None),
        ('iint', u'\N{DOUBLE INTEGRAL}', None),
        ('iiint', u'\N{TRIPLE INTEGRAL}', None),
        ('oint', u'\N{CONTOUR INTEGRAL}', None),

        ('sim', u'\N{TILDE OPERATOR}', None),
        ('backsim', u'\N{REVERSED TILDE}', None),
        ('simeq', u'\N{ASYMPTOTICALLY EQUAL TO}', None),
        ('approx', u'\N{ALMOST EQUAL TO}', None),
        ('neq', u'\N{NOT EQUAL TO}', None),
        ('equiv', u'\N{IDENTICAL TO}', None),
        ('ge', u'>', None),#
        ('le', u'<', None),#
        ('leq', u'\N{LESS-THAN OR EQUAL TO}', None),
        ('geq', u'\N{GREATER-THAN OR EQUAL TO}', None),
        ('leqslant', u'\N{LESS-THAN OR EQUAL TO}', None),
        ('geqslant', u'\N{GREATER-THAN OR EQUAL TO}', None),
        ('leqq', u'\N{LESS-THAN OVER EQUAL TO}', None),
        ('geqq', u'\N{GREATER-THAN OVER EQUAL TO}', None),
        ('lneqq', u'\N{LESS-THAN BUT NOT EQUAL TO}', None),
        ('gneqq', u'\N{GREATER-THAN BUT NOT EQUAL TO}', None),
        ('ll', u'\N{MUCH LESS-THAN}', None),
        ('gg', u'\N{MUCH GREATER-THAN}', None),
        ('nless', u'\N{NOT LESS-THAN}', None),
        ('ngtr', u'\N{NOT GREATER-THAN}', None),
        ('nleq', u'\N{NEITHER LESS-THAN NOR EQUAL TO}', None),
        ('ngeq', u'\N{NEITHER GREATER-THAN NOR EQUAL TO}', None),
        ('lesssim', u'\N{LESS-THAN OR EQUIVALENT TO}', None),
        ('gtrsim', u'\N{GREATER-THAN OR EQUIVALENT TO}', None),
        ('lessgtr', u'\N{LESS-THAN OR GREATER-THAN}', None),
        ('gtrless', u'\N{GREATER-THAN OR LESS-THAN}', None),
        ('prec', u'\N{PRECEDES}', None),
        ('succ', u'\N{SUCCEEDS}', None),
        ('preceq', u'\N{PRECEDES OR EQUAL TO}', None),
        ('succeq', u'\N{SUCCEEDS OR EQUAL TO}', None),
        ('precsim', u'\N{PRECEDES OR EQUIVALENT TO}', None),
        ('succsim', u'\N{SUCCEEDS OR EQUIVALENT TO}', None),
        ('nprec', u'\N{DOES NOT PRECEDE}', None),
        ('nsucc', u'\N{DOES NOT SUCCEED}', None),
        ('subset', u'\N{SUBSET OF}', None),
        ('supset', u'\N{SUPERSET OF}', None),
        ('subseteq', u'\N{SUBSET OF OR EQUAL TO}', None),
        ('supseteq', u'\N{SUPERSET OF OR EQUAL TO}', None),
        ('nsubseteq', u'\N{NEITHER A SUBSET OF NOR EQUAL TO}', None),
        ('nsupseteq', u'\N{NEITHER A SUPERSET OF NOR EQUAL TO}', None),
        ('subsetneq', u'\N{SUBSET OF WITH NOT EQUAL TO}', None),
        ('supsetneq', u'\N{SUPERSET OF WITH NOT EQUAL TO}', None),

        ('cdot', u'\N{MIDDLE DOT}', None),
        ('times', u'\N{MULTIPLICATION SIGN}', None),
        ('otimes', u'\N{CIRCLED TIMES}', None),
        ('oplus', u'\N{CIRCLED PLUS}', None),
        ('bigotimes', u'\N{CIRCLED TIMES}', None),
        ('bigoplus', u'\N{CIRCLED PLUS}', None),

        ('frac', '%s/%s', None),
        ('nicefrac', '%s/%s', None),

        ('cos', 'cos', None),
        ('sin', 'sin', None),
        ('tan', 'tan', None),
        ('arccos', 'arccos', None),
        ('arcsin', 'arcsin', None),
        ('arctan', 'arctan', None),
        ('cosh', 'cosh', None),
        ('sinh', 'sinh', None),
        ('tanh', 'tanh', None),
        ('arccosh', 'arccosh', None),
        ('arcsinh', 'arcsinh', None),
        ('arctanh', 'arctanh', None),
        
        ('ln', 'ln', None),
        ('log', 'log', None),

        ('max', 'max', None),
        ('min', 'min', None),
        ('sup', 'sup', None),
        ('inf', 'inf', None),
        ('lim', 'lim', None),
        ('limsup', 'lim sup', None),
        ('liminf', 'lim inf', None),

        ('prime', "'", None),
        ('dag', u"\N{DAGGER}", None),
        ('dagger', u"\N{DAGGER}", None),
        ('pm', u"\N{PLUS-MINUS SIGN}", None),
        ('mp', u"\N{MINUS-OR-PLUS SIGN}", None),

        (',', u" ", None),
        (';', u" ", None),
        (':', u" ", None),
        (' ', u" ", None),
        ('!', u"", None), # sorry, no negative space in ascii
        ('quad', u"  ", None),
        ('qquad', u"    ", None),

        ('ldots', u"...", None),
        ('cdots', u"...", None),
        ('ddots', u"...", None),
        ('dots', u"...", None),

        ('langle', u'\N{LEFT ANGLE BRACKET}', None),
        ('rangle', u'\N{RIGHT ANGLE BRACKET}', None),
        ('lvert', u'|', None),
        ('rvert', u'|', None),
        ('vert', u'|', None),
        ('lVert', u'\u2016', None),
        ('rVert', u'\u2016', None),
        ('Vert', u'\u2016', None),
        ('mid', u'|', None),
        ('nmid', u'\N{DOES NOT DIVIDE}', None),

        ('ket', u'|%s\N{RIGHT ANGLE BRACKET}', None),
        ('bra', u'\N{LEFT ANGLE BRACKET}%s|', None),
        ('braket', u'\N{LEFT ANGLE BRACKET}%s|%s\N{RIGHT ANGLE BRACKET}', None),
        ('ketbra', u'|%s\N{RIGHT ANGLE BRACKET}\N{LEFT ANGLE BRACKET}%s|', None),
        ('uparrow', u'\N{UPWARDS ARROW}', None),
        ('downarrow', u'\N{DOWNWARDS ARROW}', None),
        ('rightarrow', u'\N{RIGHTWARDS ARROW}', None),
        ('to', u'\N{RIGHTWARDS ARROW}', None),
        ('leftarrow', u'\N{LEFTWARDS ARROW}', None),
        ('longrightarrow', u'\N{LONG RIGHTWARDS ARROW}', None),
        ('longleftarrow', u'\N{LONG LEFTWARDS ARROW}', None),

        # we use these conventions as Identity operator (\mathbbm{1})
        ('id', u'\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL I}', None),
        ('Ident', u'\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL I}', None),
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
        'specials': [
            SpecialsTextSpec('~', u"\N{NO-BREAK SPACE}"),
            SpecialsTextSpec('``', u"\N{LEFT DOUBLE QUOTATION MARK}"),
            SpecialsTextSpec("''", u"\N{RIGHT DOUBLE QUOTATION MARK}"),
            SpecialsTextSpec("--", u"\N{EN DASH}"),
            SpecialsTextSpec("---", u"\N{EM DASH}"),
            SpecialsTextSpec("!`", u"\N{INVERTED EXCLAMATION MARK}"),
            SpecialsTextSpec("?`", u"\N{INVERTED QUESTION MARK}"),
        ]
    }),
]





def _greekletters(letterlist):
    for l in letterlist:
        ucharname = l.upper()
        if ucharname == 'LAMBDA':
            ucharname = 'LAMDA'
        smallname = "GREEK SMALL LETTER "+ucharname
        if ucharname == 'EPSILON':
            smallname = "GREEK LUNATE EPSILON SYMBOL"
        if ucharname == 'PHI':
            smallname = "GREEK PHI SYMBOL"
        latex_base_specs['macros'].append(
            MacroTextSpec(l, unicodedata.lookup(smallname))
        )
        latex_base_specs['macros'].append(
            MacroTextSpec(l[0].upper()+l[1:], unicodedata.lookup("GREEK CAPITAL LETTER "+ucharname))
            )
_greekletters(
    ('alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa',
     'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi',
     'chi', 'psi', 'omega')
)
latex_base_specs['macros'] += [
    MacroTextSpec('varepsilon', u'\N{GREEK SMALL LETTER EPSILON}'),
    MacroTextSpec('vartheta', u'\N{GREEK THETA SYMBOL}'),
    MacroTextSpec('varpi', u'\N{GREEK PI SYMBOL}'),
    MacroTextSpec('varrho', u'\N{GREEK RHO SYMBOL}'),
    MacroTextSpec('varsigma', u'\N{GREEK SMALL LETTER FINAL SIGMA}'),
    MacroTextSpec('varphi', u'\N{GREEK SMALL LETTER PHI}'),
    ]


unicode_accents_list = (
    # see http://en.wikibooks.org/wiki/LaTeX/Special_Characters for a list
    ("'", u"\N{COMBINING ACUTE ACCENT}"),
    ("`", u"\N{COMBINING GRAVE ACCENT}"),
    ('"', u"\N{COMBINING DIAERESIS}"),
    ("c", u"\N{COMBINING CEDILLA}"),
    ("^", u"\N{COMBINING CIRCUMFLEX ACCENT}"),
    ("~", u"\N{COMBINING TILDE}"),
    ("H", u"\N{COMBINING DOUBLE ACUTE ACCENT}"),
    ("k", u"\N{COMBINING OGONEK}"),
    ("=", u"\N{COMBINING MACRON}"),
    ("b", u"\N{COMBINING MACRON BELOW}"),
    (".", u"\N{COMBINING DOT ABOVE}"),
    ("d", u"\N{COMBINING DOT BELOW}"),
    ("r", u"\N{COMBINING RING ABOVE}"),
    ("u", u"\N{COMBINING BREVE}"),
    ("v", u"\N{COMBINING CARON}"),

    ("vec", u"\N{COMBINING RIGHT ARROW ABOVE}"),
    ("dot", u"\N{COMBINING DOT ABOVE}"),
    ("hat", u"\N{COMBINING CIRCUMFLEX ACCENT}"),
    ("check", u"\N{COMBINING CARON}"),
    ("breve", u"\N{COMBINING BREVE}"),
    ("acute", u"\N{COMBINING ACUTE ACCENT}"),
    ("grave", u"\N{COMBINING GRAVE ACCENT}"),
    ("tilde", u"\N{COMBINING TILDE}"),
    ("bar", u"\N{COMBINING OVERLINE}"),
    ("ddot", u"\N{COMBINING DIAERESIS}"),

    ("not", u"\N{COMBINING LONG SOLIDUS OVERLAY}"),

    )

def make_accented_char(node, combining, l2tobj):
    if len(node.nodeargs):
        nodearg = node.nodeargs[0]
        c = l2tobj.nodelist_to_simplified([nodearg]).strip()
    else:
        c = ' '

    def getaccented(ch, combining):
        ch = unicode(ch)
        combining = unicode(combining)
        if (ch == u"\N{LATIN SMALL LETTER DOTLESS I}"):
            ch = u"i"
        if (ch == u"\N{LATIN SMALL LETTER DOTLESS J}"):
            ch = u"j"
        #print u"Accenting %s with %s"%(ch, combining) # this causes UnicdeDecodeError!!!
        return unicodedata.normalize('NFC', unicode(ch)+combining)

    return u"".join([getaccented(ch, combining) for ch in c])


for u in unicode_accents_list:
    (mname, mcombining) = u
    latex_base_specs['macros'].append(
        MacroTextSpec(mname, lambda x, l2tobj, c=mcombining: make_accented_char(x, c, l2tobj))
    )

# specs structure now complete
