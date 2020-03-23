# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

r"""
A simplistic LaTeX code parser with the ability further simplify the resulting TeX code.

The main class is :py:class:`LatexSimplifier`. For a quick start, try::

  from texparser.texsimplifier import LatexSimplifier

  latex = "... LaTeX code ..."
  simplified = LatexSimplifier().simplify(latex)

You may also use the command-line version of `texsimplifier`::

  $ echo '\textit{italic} \begin{tabular}...\end{tabular} \`acc\^ented text' | texsimplifier
  \textit{italic} \`acc\^ented text
"""

from __future__ import print_function, unicode_literals

import os
import re
import logging
import sys
import inspect
import textwrap

if sys.version_info.major >= 3:
  def unicode(string): return string
  basestring = str
  getfullargspec = inspect.getfullargspec
else:
  getfullargspec = inspect.getargspec

import texparser
from texparser import texwalker
from texparser import macrospec
from texparser.utils import util

logger = logging.getLogger(__name__)






class MacroTextSpec(object):
  """
  A specification of how to obtain a textual representation of a macro.

  .. py:attribute:: macroname

      The name of the macro (no backslash)

  .. py:attribute:: simplify_repl

      The replacement text of the macro invocation.  This is either a string or
      a callable:

        - If `simplify_repl` is a string, it may contain '%s' replacements, in
          which the macro arguments will be substituted in the given order.
          The string may instead contain '%(<n>)s' (where `<n>` is an integer)
          to refer to the n-th argument (starting at '%(1)s').  You cannot mix
          the two %-formatting styles.

        - If `simplify_repl` is a callable, it should accept the corresponding
          :py:class:`pylatexenc.latexwalker.LatexMacroNode` as an argument.  If
          the callable expects a second argument named `l2tobj`, then the
          `LatexNodes2Text` object is provided to that argument.

  .. py:attribute:: discard
  
      If set to `True`, then the macro call is discarded, i.e., it is converted
      to an empty string.


  .. versionadded:: 2.0

      The class :py:class:`MacroTextSpec` was introduced in `pylatexenc
      2.0` to succeed to the previously named `MacroDef` class.
  """
  def __init__(self, macroname, simplify_repl=None, discard=None, n=None):
    super(MacroTextSpec, self).__init__()
    self.macroname = macroname
    if simplify_repl != None:
      self.discard = False
    if discard != None:
      self.discard = discard
    #self.discard = True if (discard is None) else discard
    self.simplify_repl = simplify_repl
    self.n = n

    #if self.n != None:
    #  print("n: {}".format(self.n))


class EnvironmentTextSpec(object):
  """
  A specification of how to obtain a textual representation of an environment.

  .. py:attribute:: environmentname

      The name of the environment

  .. py:attribute:: simplify_repl

      The replacement text of the environment.  This is either a string or a
      callable:

        - If `simplify_repl` is a string, it may contain a single '%s'
          replacements, in which the (processed) environment body will be substituted.

          The `simplify_repl` string may instead contain '%(<n>)s' (where `<n>`
          is an integer) to refer to the n-th argument after
          ``\begin{environment}`` (starting at '%(1)s').  The body of the
          environment has to be referred to with `%(body)s`.

          You cannot mix the two %-formatting styles.

        - If `simplify_repl` is a callable, it should accept the corresponding
          :py:class:`pylatexenc.latexwalker.LatexEnvironmentNode` as an
          argument.  If the callable expects a second argument named `l2tobj`,
          then the `LatexNodes2Text` object is provided to that argument.

  .. py:attribute:: discard
  
      If set to `True`, then the full environment is discarded, i.e., it is
      converted to an empty string.


  .. versionadded:: 2.0

      The class :py:class:`EnvironmentTextSpec` was introduced in `pylatexenc
      2.0` to succeed to the previously named `EnvDef` class.
  """
  def __init__(self, environmentname, simplify_repl=None, discard=False, n=None):
    super(EnvironmentTextSpec, self).__init__()
    self.environmentname = environmentname
    self.simplify_repl = simplify_repl
    self.discard = discard
    self.n = n

    #if self.n != None:
    #  print("n: {}".format(self.n))


class SpecialsTextSpec(object):
  """
  A specification of how to obtain a textual representation of latex specials.

  .. py:attribute:: specials_chars
  
      The sequence of special LaTeX characters

  .. py:attribute:: simplify_repl

      The replacement text for the given latex specials.  This is either a
      string or a callable:

        - If `simplify_repl` is a string, it may contain '%s' replacements, in
          which the macro arguments will be substituted in the given order.
          The string may instead contain '%(<n>)s' (where `<n>` is an integer)
          to refer to the n-th argument (starting at '%(1)s').  You cannot mix
          the two %-formatting styles.

        - If `simplify_repl` is a callable, it should accept the corresponding
          :py:class:`pylatexenc.latexwalker.LatexMacroNode` as an argument.  If
          the callable expects a second argument named `l2tobj`, then the
          `LatexNodes2Text` object is provided to that argument.

  .. versionadded:: 2.0

      Latex specials were introduced in `pylatexenc 2.0`.
  """
  def __init__(self, specials_chars, simplify_repl=None):
    super(SpecialsTextSpec, self).__init__()
    self.specials_chars = specials_chars
    self.simplify_repl = simplify_repl



def fmt_replace_documentclass(envnode, l2tobj):
  if envnode.nodeargd and envnode.nodeargd.argnlist:
    a = envnode.nodeargd.argnlist
  return "\\documentclass{article}\n" + \
         "\\usepackage[letterspace=51]{microtype}\n\\lsstyle\n"
  
  # "\\" + envnode.macroname + "".join([l2tobj._groupnodecontents_to_text(n) if '{' not in n.delimiters else '' for n in a]) + 
  #return envnode.macroname##l2tobj.macro_node_to_text(envnode)


def fmt_replace_begin_document(envnode, l2tobj):
  return "\\begin{document}\n\\maketitle\n"


def fmt_verb_macro(envnode, l2tobj):
  if envnode.nodeargd and envnode.nodeargd.argnlist:
    a = envnode.nodeargd.argnlist
  return "\\verb" + "".join([envnode.nodeargd.verbatim_delimiters[0] + l2tobj._groupnodecontents_to_text(n) + envnode.nodeargd.verbatim_delimiters[1] for n in a])

def fmt_equation_environment(envnode, l2tobj):
  r"""
  Can be used as callback for display equation environments.

  .. versionadded:: 2.0

      This function was introduced in `pylatexenc 2.0`.
  """

  return l2tobj.math_node_to_text(envnode)
  # with _PushEquationContext(l2tobj):
  #
  #     contents = l2tobj.nodelist_to_text(envnode.nodelist).strip()
  #     # indent equation, separate by newlines
  #     return l2tobj._fmt_indented_block(contents)


def fmt_reconstruct_macro(macronode, l2tobj):
  logger.warning("Reconstructing macro '{}' with parameters: {}".format(macronode, ""))
  return ""

def fmt_input_macro(macronode, l2tobj):
  r"""
  This function can be used as callback in :py:class:`MacroTextSpec` for
  ``\input`` or ``\include`` macros.  The `macronode` must be a macro node
  with a single argument.  If :py:meth:`set_tex_input_directory()` was called
  with a nonempty input directory in the :py:class:`LatexNodes2Text` object,
  then this method reads the contents of the file name in the macro argument
  according to the provided settings.  Otherwise, returns an empty string.

  .. versionadded:: 2.0

      This function was introduced in `pylatexenc 2.0`.
  """
  return l2tobj._input_node_simplify_repl(macronode)


def placeholder_node_formatter(placeholdertext, block=True):
  r"""
  This function returns a callable that can be used in
  :py:class:`MacroTextSpec`, :py:class:`EnvironmentTextSpec`, or
  :py:class:`SpecialsTextSpec` for latex nodes that do not have a good textual
  representation, providing as text replacement the simple placeholder text
  ``'< P L A C E H O L D E R   T E X T >'``.

  If `block=True` (the default), the placeholder text is typeset in an
  indented block on its own.  Otherwise, it is typeset inline.

  .. versionadded:: 2.0

      This function was introduced in `pylatexenc 2.0`.
  """
  return  lambda n, l2tobj, pht=placeholdertext: \
    _do_fmt_placeholder_node(pht, l2tobj, block=block)
    
def _do_fmt_placeholder_node(placeholdertext, l2tobj, block=True):
  # spaces added so that database indexing doesn't index the word "array" or
  # "pmatrix"
  txt = '< ' + " ".join(placeholdertext) + ' >'
  if block:
    return l2tobj._fmt_indented_block(txt, indent='    ')
  return ' ' + txt + ' '

def fmt_placeholder_node(node, l2tobj):
  r"""
  This function can be used as callable in :py:class:`MacroTextSpec`,
  :py:class:`EnvironmentTextSpec`, or :py:class:`SpecialsTextSpec` for latex
  nodes that do not have a good textual representation.  The text replacement
  is the placeholder text
  ``'< N A M E   O F   T H E   M A C R O   O R   E N V I R O N M E N T >'``.

  .. versionadded:: 2.0

      This function was introduced in `pylatexenc 2.0`.
  """

  for att in ('macroname', 'environmentname', 'specials_chars'):
    if hasattr(node, att):
      name = getattr(node, att)
      break
  else:
    name = '<unknown>'

  return _do_fmt_placeholder_node(name, l2tobj)






def get_default_latex_context_db():
  r"""
  Return a :py:class:`pylatexenc.macrospec.LatexContextDb` instance
  initialized with a collection of text replacements for known macros and
  environments.

  TODO: clean up and document categories.

  If you want to add your own definitions, you should use the
  :py:meth:`pylatexenc.macrospec.LatexContextDb.add_context_category()`
  method.  If you would like to override some definitions, use that method
  with the argument `prepend=True`.  See docs for
  :py:meth:`pylatexenc.macrospec.LatexContextDb.add_context_category()`.

  If there are too many macro/environment definitions, or if there are some
  irrelevant ones, you can always filter the returned database using
  :py:meth:`pylatexenc.macrospec.LatexContextDb.filter_context()`.

  .. versionadded:: 2.0

      The :py:class:`pylatexenc.macrospec.LatexContextDb` class as well as this
      method, were all introduced in `pylatexenc 2.0`.
  """
  db = macrospec.LatexContextDb()
  
  from texparser.texsimplifier.default_specs import specs

  for cat, catspecs in specs:
    db.add_context_category(cat,
                            macros=catspecs['macros'],
                            environments=catspecs['environments'],
                            specials=catspecs['specials'])
  
  return db


default_macro_dict = util.LazyDict(
  generate_dict_fn=lambda: dict([
    (m.macroname, m)
    for m in get_default_latex_context_db().iter_macro_specs()
  ])
)
r"""
.. deprecated:: 2.0

   Use :py:func:`get_default_latex_context_db()` instead, or create your own
   :py:class:`pylatexenc.macrospec.LatexContextDb` object.


Provide an access to the default macro text replacement specs for `latex2text`
in a form that is compatible with `pylatexenc 1.x`\ 's `default_macro_dict`
module-level dictionary.

This is implemented using a custom lazy mutable mapping, which behaves just like
a regular dictionary but that loads the data only once the dictionary is
accessed.  In this way the default latex specs into a python dictionary unless
they are actually queried or modified, and thus users of `pylatexenc 2.0` that
don't rely on the default macro/environment definitions shouldn't notice any
decrease in performance.
"""

default_env_dict = util.LazyDict(
  generate_dict_fn=lambda: dict([
    (m.environmentname, m)
    for m in get_default_latex_context_db().iter_environment_specs()
  ])
)
r"""
.. deprecated:: 2.0

   Use :py:func:`get_default_latex_context_db()` instead, or create your own
   :py:class:`pylatexenc.macrospec.LatexContextDb` object.


Provide an access to the default environment text replacement specs for
`latex2text` in a form that is compatible with `pylatexenc 1.x`\ 's
`default_macro_dict` module-level dictionary.

This is implemented using a custom lazy mutable mapping, which behaves just like
a regular dictionary but that loads the data only once the dictionary is
accessed.  In this way the default latex specs into a python dictionary unless
they are actually queried or modified, and thus users of `pylatexenc 2.0` that
don't rely on the default macro/environment definitions shouldn't notice any
decrease in performance.
"""


# ------------------------------------------------------------------------------

_strict_latex_spaces_predef = {
  'based-on-source': {
    'between-macro-and-chars': False,
    'between-latex-constructs': False,
    'after-comment': False,
    'in-equations': None,
  },
  'macros': {
    'between-macro-and-chars': True,
    'between-latex-constructs': True,
    'after-comment': False,
    'in-equations': False,
  },
  'except-in-equations': {
    'between-macro-and-chars': True,
    'between-latex-constructs': True,
    'after-comment': True,
    'in-equations': False,
  },
}
# compatibility with pylatexenc 1.x, but it is no longer the default!!
_strict_latex_spaces_predef['default'] = _strict_latex_spaces_predef['based-on-source']



def _parse_strict_latex_spaces_dict(strict_latex_spaces):
  d = {
    'between-macro-and-chars': False,
    'between-latex-constructs': False,
    'after-comment': False,
    'in-equations': None,
  }
  if strict_latex_spaces is None:
    return d
  elif isinstance(strict_latex_spaces, dict):
    d.update(strict_latex_spaces)
    return d
  elif isinstance(strict_latex_spaces, basestring):
    if strict_latex_spaces == 'on':
      return _parse_strict_latex_spaces_dict(True)
    if strict_latex_spaces == 'off':
      return _parse_strict_latex_spaces_dict(False)
    if strict_latex_spaces not in _strict_latex_spaces_predef:
      raise ValueError("invalid value for strict_latex_spaces preset: {}"
                        .format(strict_latex_spaces))

    if strict_latex_spaces == 'default': # deprecated -- report this
      util.pylatexenc_deprecated_2(
        "The value 'default' for `strict_latex_spaces=` in LatexNodes2Text() is deprecated. "
        "The actual default changed to 'macros', and for backwards compatibility the "
        "obsolete value 'default' still refers to the earlier default which is now called "
        "'based-on-source'.",
        stacklevel=4
      )

    return _strict_latex_spaces_predef[strict_latex_spaces]
  else:
    for k in d.keys():
      d[k] = bool(strict_latex_spaces)
    return d


class LatexSimplifier(object):
  r"""
  """
  def __init__(self, latex_context=None, **flags):
    # Call super class
    super(LatexSimplifier, self).__init__()

    # Initialize latex context
    if latex_context is None:
      latex_context = get_default_latex_context_db()

    self.latex_context = latex_context

    self.tex_input_directory = None
    self.strict_input = True

    # Keep math?
    self.math_mode = flags.pop('math_mode', 'text')

    self.keep_comments = flags.pop('keep_comments', False)

    strict_latex_spaces = flags.pop('strict_latex_spaces', False)
    self.strict_latex_spaces = _parse_strict_latex_spaces_dict(strict_latex_spaces)

    self.keep_braced_groups = flags.pop('keep_braced_groups', False)
    self.keep_braced_groups_minlen = flags.pop('keep_braced_groups_minlen', 2)

    self.fill_text = flags.pop('fill_text', None)

  def set_tex_input_directory(
    self,
    tex_input_directory,
    latex_walker_init_args=None,
    strict_input=True
  ):
    """
    Sets where to look for input files when encountering the ``\\input`` or ``\\include`` macro.
    """
    self.tex_input_directory = tex_input_directory
    self.latex_walker_init_args = latex_walker_init_args if latex_walker_init_args else {}
    self.strict_input = strict_input

  def read_input_file(
    self,
    fn
  ):
    """
    """
    # If there is no input directory, just return an empty string
    if self.tex_input_directory is None:
      return ""

    fnfull = os.path.realpath(os.path.join(self.tex_input_directory, fn))

    if self.strict_input:
      # make sure that the input file is strictly within dirfull and didn't escape with
      # "../.." tricks or vial symlink
      dirfull = os.path.realpath(self.tex_input_directory)
      if not fnfull.startswith(dirfull):
        logger.warning(
          "Can't access path '%s' leading outside of mandated directory [strict input mode", fn
        )
        return ""

    if not os.path.exists(fnfull) and os.path.exists(fnfull + ".tex"):
      fnfull = fnfull + ".tex"
    if not os.path.exists(fnfull) and os.path.exists(fnfull + ".latex"):
      fnfull = fnfull + ".latex"
    if not os.path.isfile(fnfull):
      logger.warning(u"Error, file does not exist: '%s", fn)
      return ""

    logger.debug("Reading input file %r", fnfull)

    try:
      with open(fnfull) as fin:
        return fin.read()
    except IOError as e:
      logger.warning(u"Error, cannot access file '%s': %s", fn, e)
      return ""

  def _input_node_simplify_repl(self, n):
    
    if len(n.nodeargs) != 1:
      logger.warning(u"Expected exactly one argument for '\\input' ! Got = %r", n.nodeargs)

    input_tex = self.read_input_file(self.nodelist_to_simplified([n.nodeargs[0]]).strip())

    if not input_tex:
      return ""

    return self.nodelist_to_simplified(
      texwalker.LatexWalker(input_tex, **self.latex_walker_init_args).get_latex_nodes()[0]
    )


  def latex_to_simplified(self, latex, **parse_flags):
    return self.nodelist_to_simplified(texwalker.LatexWalker(latex, **parse_flags).get_latex_nodes()[0])

  def nodelist_to_simplified(self, nodelist):
    s = ''
    prev_node = None
    for node in nodelist:
      if self._is_bare_macro_node(prev_node) and node.isNodeType(texwalker.LatexCharsNode):
        if not self.strict_latex_spaces['between-macro-and-chars']:
          # after a macro with absolutely no arguments, include
          # post_space in output by default if there are other chars
          # that follow.  This is for more breathing space (especially
          # in equations(?)), and for compatibility with earlier
          # versions of pylatexenc (<= 1.3).  This is NOT LaTeX'
          # default behavior (see issue #11), so only do this if the
          # corresponding `strict_latex_spaces=` flag is set.
          s += prev_node.macro_post_space

      last_nl_pos = s.rfind('\n')
      if last_nl_pos != -1:
        textcol = len(s)-last_nl_pos-1
      else:
        textcol = len(s)

      s += self.node_to_text(node, textcol=textcol)

      prev_node = node

    return s

  def node_to_text(self, node, prev_node_hint=None, textcol=0):
    if node is None:
      return ""

    # ### It doesn't look like we use prev_node_hint at all.  Eliminate at
    # ### some point?
    
    if node.isNodeType(texwalker.LatexCharsNode):
      return self.chars_node_to_text(node, textcol=textcol)
    
    if node.isNodeType(texwalker.LatexCommentNode):
      return self.comment_node_to_text(node)
    
    if node.isNodeType(texwalker.LatexGroupNode):
      return self.group_node_to_text(node)
    
    if node.isNodeType(texwalker.LatexMacroNode):
      return self.macro_node_to_text(node)
    
    if node.isNodeType(texwalker.LatexEnvironmentNode):
      return self.environment_node_to_text(node)

    if node.isNodeType(texwalker.LatexSpecialsNode):
      return self.specials_node_to_text(node)

    if node.isNodeType(texwalker.LatexMathNode):
      return self.math_node_to_text(node)

    logger.warning("LatexSimplifier.node_to_text(): Unknown node: %r", node)

    # discard anything else.
    return ""


  def chars_node_to_text(self, node, textcol=0):
    
    content = node.chars

    if self.fill_text:
      content = self.do_fill_text(content, textcol=textcol)
    
    if not self.strict_latex_spaces["between-latex-constructs"] and len(content.strip()) == 0:
      return ""

    return content

  def comment_node_to_text(self, node):
    
    if self.keep_comments:
      if self.strict_latex_spaces["after-comment"]:
        nl = "\n"
        if node.comment_post_space == "":
          nl = ""
        return node.comment + nl
      else:
        return "%" + node.comment + node.comment_post_space
    
    else:
      if self.strict_latex_spaces["after-comment"]:
        return ""
      else:
        return node.comment_post_space

  def group_node_to_text(self, node):
    
    contents = self._groupnodecontents_to_text(node)

    if self.keep_braced_groups and len(contents) >= self.keep_braced_groups_minlen:
      return contents
    return contents

  def macro_node_to_text(self, node):
    macroname = node.macroname
    mac = self.latex_context.get_macro_spec(macroname)

    if mac is None:
      #default to unknown macros, which will be fully eliminated
      mac = MacroTextSpec(macroname, discard=True)
    
    def get_macro_str_repl(node, macroname, mac):
      if mac.discard:
        return ""

      if mac.simplify_repl:
        return self.apply_simplify_repl(node, mac.simplify_repl, what=r"macro '\%s'"%(macroname))
      
      a = []

      if node.nodeargd and node.nodeargd.argnlist:
        a = node.nodeargd.argnlist
      return "\\" + mac.macroname + "".join([self._groupnodecontents_to_text(n) for n in a])
    
    macrostr = get_macro_str_repl(node, macroname, mac)

    if mac.macroname == "shortauthors":
      logger.warning("IDENTIFIED SHORTAUTHORS: {}".format(macrostr))

    return macrostr

  def environment_node_to_text(self, node):
    environmentname = node.environmentname
    envdef = self.latex_context.get_environment_spec(environmentname)
    if envdef is None:
      # default for unknown environments
      envdef = EnvironmentTextSpec(environmentname, discard=True)

    if envdef.simplify_repl:
      return self.apply_simplify_repl(node, envdef.simplify_repl,
                                      what="environment '%s'"%(environmentname))
    if envdef.discard:
      return ""

    return "\\begin{" + envdef.environmentname + "}\n" + self.nodelist_to_simplified(node.nodelist) + "\n\\end{" + envdef.environmentname + "}\n"

  def specials_node_to_text(self, node):
    specials_chars = node.specials_chars
    sspec = self.latex_context.get_specials_spec(specials_chars)
    if sspec is None:
      # no corresponding spec, leave the special chars unchanged:
      return specials_chars

    def get_specials_str_repl(node, specials_chars, spec):
      if spec.simplify_repl:
        return self.apply_simplify_repl(node, spec.simplify_repl,
                                        what="specials '%s'"%(specials_chars))
      if spec.discard:
        return ""
      if node.nodeargd and node.nodeargd.argnlist:
        a = node.nodeargd.argnlist
      return "".join([self._groupnodecontents_to_text(n) for n in a])

    s = get_specials_str_repl(node, specials_chars, sspec)
    return s

  def math_node_to_text(self, node):
    if self.math_mode == 'verbatim':
      if node.isNodeType(texwalker.LatexEnvironmentNode) or node.displaytype == 'display':
        return self._fmt_indented_block(node.latex_verbatim(), indent='')
      else:
        return node.latex_verbatim()

    elif self.math_mode == 'remove':
      return ''

    elif self.math_mode == 'with-delimiters':
      with _PushEquationContext(self):
        content = self.nodelist_to_simplified(node.nodelist).strip()
      if node.isNodeType(texwalker.LatexMathNode):
        delims = node.delimiters
      else: # environment node
        delims = r'\begin{%s}'%(node.environmentname), r'\end{%s}'%(node.environmentname)
      if node.isNodeType(texwalker.LatexEnvironmentNode) or node.displaytype == 'display':
        return delims[0] + self._fmt_indented_block(content, indent='') + delims[1]
      else:
        return delims[0] + content + delims[1]

    elif self.math_mode == 'text':
      with _PushEquationContext(self):
        content = self.nodelist_to_simplified(node.nodelist).strip()
      if node.isNodeType(texwalker.LatexEnvironmentNode) or node.displaytype == 'display':
        return self._fmt_indented_block(content)
      else:
        return content

    else:
        raise RuntimeError("unknown math_mode={} !".format(self.math_mode))



  def do_fill_text(self, text, textcol=0):
    # keep trailing whitespace to have whitespace between macros in text 
    head_ws = re.search(r'^\s*', text).group()
    head_par = '\n\n' if ('\n\n' in head_ws) else ''
    #head_nl = '\n' if (not head_par and '\n' in head_ws) else ''
    trail_ws = re.search(r'\s*$', text).group()
    trail_par = '\n\n' if ('\n\n' in trail_ws) else ''
    #trail_nl = '\n' if (not trail_par and '\n' in trail_ws) else ''
    text = text.strip()
    def fill_chunk(x, textcol):
      #head_ws = ' ' if textcol>0 and x[0:1].isspace() else ''
      #trail_ws = ' ' if x[-1:].isspace() else ''
      head_ws, trail_ws = '', ''
      x = x.strip()
      if textcol >= self.fill_text-4:
        return '\n' + textwrap.fill(x, self.fill_text) + trail_ws
      else:
        return head_ws + \
          textwrap.fill(x, self.fill_text, initial_indent='X'*textcol)[textcol:] + \
          trail_ws
    return head_par + (' ' if textcol>0 and head_ws and not head_par else '') + "\n\n".join(
      chunk
      for chunk in (fill_chunk(x, textcol if j==0 else 0)
                    for j, x in enumerate(re.compile(r'\n{2,}').split(text)))
      if chunk.strip()
    ) + (' ' if trail_ws and not trail_par else '') + trail_par

  def apply_simplify_repl(self, node, simplify_repl, what):
    r"""
    Utility to get the replacement text associated with a `node` for which we
    have a `simplify_repl` object (given by e.g. a MacroTextSpec or
    similar).

    The argument `nodelistargs` is a list of nodes (or `None`) that
    represent the macro/environment/specials arguments.  The argument `what`
    is used in error messages.
    """
    if callable(simplify_repl):
      if 'l2tobj' in getfullargspec(simplify_repl)[0]:
        # callable accepts an argument named 'l2tobj', provide pointer to self
        r = simplify_repl(node, l2tobj=self)
      else:
        r = simplify_repl(node)
      return r if r else '' # don't return None

    if '%' in simplify_repl:
      nodeargs = []
      if node.nodeargd and node.nodeargd.argnlist:
        nodeargs = node.nodeargd.argnlist

      has_percent_s = re.search('(^|[^%])(%%)*%s', simplify_repl)

      if node.isNodeType(texwalker.LatexEnvironmentNode):
        if has_percent_s:
          x = (self.nodelist_to_simplified(node.nodelist), )
        else:
          x = dict(
            (str(1+j),val) for j, val in enumerate(
              self._groupnodecontents_to_text(nn) for nn in nodeargs
            )
          )
          x.update(body=self.nodelist_to_simplified(node.nodelist))
      elif has_percent_s:
        x = tuple([self._groupnodecontents_to_text(nn)
                    for nn in nodeargs])
      else:
        x = dict(
          (str(1+j),val) for j, val in enumerate(
            self._groupnodecontents_to_text(nn) for nn in nodeargs
          )
        )

      try:
        return simplify_repl % x
      except (TypeError, ValueError):
        logger.warning(
          "WARNING: Error in configuration: {} failed its substitution!".format(what)
        )
        return simplify_repl # too bad, keep the percent signs as they are...
    return simplify_repl

  def _fmt_indented_block(self, contents, indent=' '*4):
    block = ("\n"+indent + contents.replace("\n", "\n"+indent) + "\n")
    if self.fill_text:
      block = '\n'+block+'\n' # additional newlines because neighboring text gets trimmed
    return block
  

  def _is_bare_macro_node(self, node):
    return (node is not None and
            node.isNodeType(texwalker.LatexMacroNode) and 
            node.nodeoptarg is None and 
            len(node.nodeargs) == 0)

  def _groupnodecontents_to_text(self, groupnode):
    if groupnode is None:
      return ''
    if not groupnode.isNodeType(texwalker.LatexGroupNode):
      return self.node_to_text(groupnode)
    return groupnode.delimiters[0] + self.nodelist_to_simplified(groupnode.nodelist) + groupnode.delimiters[1]

  def node_arg_to_text(self, node, k):
    r"""
    Return the textual representation of the `k`\ -th argument of the given
    `node`.  This might be useful for substitution lambdas in macro and
    environment specs.
    """
    if node.nodeargd and node.nodeargd.argnlist:
      return self._groupnodecontents_to_text(node.nodeargd.argnlist[k])
    return ''

  def apply_text_replacements(self, s, text_replacements):
    r"""
    Convenience function for code that used `text_replacements=` in `pylatexenc
    1.x`.

    If you used custom `text_replacements=` in `pylatexenc 1.x` then you
    will have to change::

      # pylatexenc 1.x with text_replacements
      text_replacements = ...
      l2t = LatexNodes2Text(..., text_replacements=text_replacements)
      text = l2t.nodelist_to_text(...)

    to::

      # pylatexenc 2 text_replacements compatibility code
      text_replacements = ...
      l2t = LatexNodes2Text(...)
      temp = l2t.nodelist_to_text(...)
      text = l2t.apply_text_replacements(temp, text_replacements)

    as a quick fix.  It is recommended however to treat text replacements
    instead as "latex specials".  (Otherwise the brutal text replacements
    might act on text generated from macros and environments and give
    unwanted results.)  See :py:class:`pylatexenc.macrospec.SpecialsSpec`
    and :py:class:`SpecialsTextSpec`.

    .. deprecated:: 2.0

        The `apply_text_replacements()` method was introduced in `pylatexenc
        2.0` as a deprecated method.  You can use it as a quick fix to make
        existing code run as it did in `pylatexenc 1.x`.  Its use is however
        not recommended for new code.  You should use "latex specials"
        instead for characters that have special LaTeX meaning.
    """
    
    # perform suitable replacements
    for pattern, replacement in text_replacements:
      if hasattr(pattern, 'sub'):
        s = pattern.sub(replacement, s)
      else:
        s = s.replace(pattern, replacement)

    return s


class _PushEquationContext(texwalker._PushPropOverride):
  def __init__(self, l2t):

    new_strict_latex_spaces = None
    if l2t.strict_latex_spaces['in-equations'] is not None:
      new_strict_latex_spaces = _parse_strict_latex_spaces_dict(
        l2t.strict_latex_spaces['in-equations']
      )

    super(_PushEquationContext, self).__init__(l2t, 'strict_latex_spaces',
                                               new_strict_latex_spaces)