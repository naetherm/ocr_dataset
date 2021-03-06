# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import sys
import fileinput
import argparse
import logging

from texparser import texwalker
from texparser.texmacroexpander import TexMacroExpander
from texparser.texsimplifier import LatexSimplifier, _strict_latex_spaces_predef
from texparser.version import version_str

def main(argv=None):

  if argv is None:
    argv = sys.argv[1:]

  parser = argparse.ArgumentParser(prog='latexsimplifier', add_help=False)

  group = parser.add_argument_group("LatexWalker options")

  group.add_argument('--parser-keep-inline-math', action='store_const', const=True,
                      dest='parser_keep_inline_math', default=False,
                      help=argparse.SUPPRESS)
  group.add_argument('--no-parser-keep-inline-math', action='store_const', const=False,
                      dest='parser_keep_inline_math',
                      help=argparse.SUPPRESS)

  group.add_argument('--tolerant-parsing', action='store_const', const=True,
                      dest='tolerant_parsing', default=True)
  group.add_argument('--no-tolerant-parsing', action='store_const', const=False,
                      dest='tolerant_parsing',
                      help="Tolerate syntax errors when parsing, and attempt to continue (default yes)")

  # I'm not sure this flag is useful and if it should be exposed at all.
  # Accept it, but make it hidden.
  parser.add_argument('--strict-braces', action='store_const', const=True,
                      dest='strict_braces', default=False,
                      help=argparse.SUPPRESS)
  parser.add_argument('--no-strict-braces', action='store_const', const=False,
                      dest='strict_braces',
                      #help="Report errors for mismatching LaTeX braces (default no)"
                      help=argparse.SUPPRESS)

  group = parser.add_argument_group("LatexSimplifier options")

  group.add_argument('--text-keep-inline-math', action='store_const', const=True,
                      dest='text_keep_inline_math', default=False,
                      help=argparse.SUPPRESS)
  group.add_argument('--no-text-keep-inline-math', action='store_const', const=False,
                      dest='text_keep_inline_math',
                      help=argparse.SUPPRESS)

  group.add_argument('--math-mode', action='store', dest='math_mode',
                      choices=['text', 'with-delimiters', 'verbatim', 'remove'],
                      default='remove',
                      help="How to handle chunks of math mode LaTeX code. 'text' = convert "
                      "to text like the rest; 'with-delimiters' = same as 'text' but retain "
                      "the original math mode delimiters; 'verbatim' = keep verbatim LaTeX code; "
                      "'remove' = remove from input entirely")

  group.add_argument('--fill-text', dest='fill_text', action='store', nargs='?',
                      default=-1,
                      help="Attempt to wrap text to the given width, or 80 columns if option is "
                      "specified with no argument")

  group.add_argument('--keep-comments', action='store_const', const=True,
                      dest='keep_comments', default=True)
  group.add_argument('--no-keep-comments', action='store_const', const=False,
                      dest='keep_comments',
                      help="Keep LaTeX comments in text output (default no)")

  class ListWithHiddenItems(list):
      def __init__(self, thelist, hiddenitems):
          super(ListWithHiddenItems, self).__init__(thelist)
          self.hiddenitems = hiddenitems
      def __contains__(self, value):
          return super(ListWithHiddenItems, self).__contains__(value) \
              or value in self.hiddenitems

  strict_latex_spaces_choices = ListWithHiddenItems(
      # the list
      ['off', 'on']+list(k for k in _strict_latex_spaces_predef.keys() if k != 'default'),
      # hidden items: Value is accepted, but not shown in list of choices
      ['default']
  )

  # More options
  group.add_argument('--strict-latex-spaces', choices=strict_latex_spaces_choices,
                      dest='strict_latex_spaces', default='macros',
                      help="How to handle whitespace. See documentation for the class "
                      "LatexNodes2Text().")

  group.add_argument('--keep-braced-groups', action='store_const', const=True,
                      dest='keep_braced_groups', default=True)
  group.add_argument('--no-keep-braced-groups', action='store_const', const=False,
                      dest='keep_braced_groups',
                      help="Keep LaTeX {braced groups} in text output (default no)")

  group.add_argument('--keep-braced-groups-minlen', type=int, default=1,
                      dest='keep_braced_groups_minlen',
                      help="Only apply --keep-braced-groups to groups that contain at least "
                      "this many characters")

  group = parser.add_argument_group("General options")

  group.add_argument('-q', '--quiet', dest='logging_level', action='store_const',
                      const=logging.ERROR, default=logging.INFO,
                      help="Suppress warning messages")
  group.add_argument('-v', '--verbose', dest='logging_level', action='store_const',
                      const=logging.DEBUG,
                      help="Verbose output")
  group.add_argument('--version', action='version',
                     version='pylatexenc {}'.format(version_str),
                     help="Show version information and exit")
  group.add_argument('--help', action='help',
                      help="Show this help information and exit")


  group.add_argument('--letter-spacing', dest='letter_spacing', default=56, 
                     help="The letter spacing that should be used. default: 56.")
  group.add_argument('--sim-typewriter', dest='sim_typewriter', action='store_true', 
                     help="If activated, each text will be packed within typewriter font. default: False.")
  group.add_argument('--remove-title', dest='remove_title', action='store_true', 
                     help="If activated, the title will be fully removed. default: False.")
  group.add_argument('--no-abstract', dest='no_abstract', action='store_true', 
                     help="If activated, the abstract will be removed, if any is available. default: False.")

  parser.add_argument('files', metavar="FILE", nargs='*',
                      help='Input files (if none specified, read from stdandard input)')


  args = parser.parse_args(argv)

  logging.basicConfig()
  logging.getLogger().setLevel(args.logging_level)

  if args.parser_keep_inline_math is not None or args.text_keep_inline_math is not None:
    logging.warning("Options --parser-keep-inline-math and --text-keep-inline-math are "
                    "deprecated and no longer have any effect.  Please use "
                    "--math-mode=... instead.")

  # Call the macro expander

  for filename in args.files:
    tme = TexMacroExpander(
      input_file=filename,
      output_file=filename
    )

  latex = ''
  for line in fileinput.input(files=args.files):
    latex += line

  if args.fill_text != -1:
    if args.fill_text is not None and len(args.fill_text):
      fill_text = int(args.fill_text)
    else:
      fill_text = True
  else:
    fill_text = None

  lw = texwalker.LatexWalker(
    latex,
    tolerant_parsing=args.tolerant_parsing,
    strict_braces=args.strict_braces
  )

  (nodelist, pos, len_) = lw.get_latex_nodes()

  # TODO create the simplifier instance
  ln2s = LatexSimplifier(
    math_mode=args.math_mode,
    keep_comments=args.keep_comments,
    strict_latex_spaces=args.strict_latex_spaces,
    keep_braced_groups=args.keep_braced_groups,
    keep_braced_groups_minlen=args.keep_braced_groups_minlen,
    fill_text=fill_text,
    letter_spacing=args.letter_spacing,
    sim_typewriter=args.sim_typewriter,
    remove_title=args.remove_title,
    no_abstract=args.no_abstract
  )

  print(ln2s.nodelist_to_simplified(nodelist) + "\n")

if __name__ == '__main__':
  main()
