# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import copy
import fileinput
import regex as re

class Macro(object):

  def __init__(self, num, definition):
    self.num = num
    self.definition = definition

    #print("Created: num={}; definition={}".format(self.num, self.definition))

class TexMacroExpander(object):

  def __init__(
    self,
    **kwargs
  ):
    super(TexMacroExpander, self).__init__()

    self.input_file = kwargs.pop('input_file')
    self.output_file = kwargs.pop('output_file')

    # Read the file input
    self.latex_in = ''
    self.latex_out = ''
    with open(self.input_file, 'r', encoding='utf-8') as fin:
      self.latex_in = fin.read()
    self.latex_out = copy.deepcopy(self.latex_in)

    self.def_replacements = []
    self.env_replacements = []
    self.math_replacements = []

    self.macros = {}
    
    # Perform the expanding

    ## Fetch all macros
    #print("Start extraction ...")
    self._extract_macros()

    #print("Replace extracted macros ...")
    ## Replace all macros
    self._expand_macros()

    #print("\n"*10)
    #print("="*20)
    #print("Created the final output:")
    #print(self.latex_out)

    # Further cleanup
    split_content = self.latex_out.split("\n")
    final_output = ""
    for line in split_content:
      if line.startswith("\\") and "{" not in line:
        continue
      else:
        final_output += line + "\n"


    # Don't forget to save the file ...
    with open(self.output_file, 'w') as fout:
      fout.write(final_output)

  def _extract_macros(self):
    cs = r"\\\w+"

    # Extract all \def \gdef \edef and \xdef
    def_matches = re.findall(
      r"\\[gex]?def\*? *(" + cs + r") *(#\d)*" + self._nested_brackets(level=5), 
      self.latex_in)
    def_repl = re.compile(r"\\[gex]?def\*? *(" + cs + r") *(#\d)*" + self._nested_brackets(level=5))
    self.latex_out = re.sub(def_repl, "", self.latex_out)
    
    
    #print("DEF replacements:")
    if def_matches:
      #print(def_matches)#.groups())
      self.def_replacements = def_matches
      for d in self.def_replacements:
        if '#' in d[1]:
          pass
        else:
          m = Macro(min(int(d[1]) / 2, 9) if d[1] != '' else 0, TexMacroExpander.trim_string(d[2]))
          self.macros[TexMacroExpander.trim_string(d[0])] = m
    
    #print("="*20)
    #print("Fetched Macros:")
    #for m in self.macros:
    #  print(m)

    # Extract all \newcommand[*], \renewcommand[*]
    env_matches = re.findall(
      r"\\(?:re)?newcommand\*? *(" + cs + r"|\{" + cs + r"\}) *(\[(\d)\])?" + self._nested_brackets(level=5), 
      self.latex_in)
    env_repl = re.compile(r"\\(?:re)?newcommand\*? *(" + cs + r"|\{" + cs + r"\}) *(\[(\d)\])?" + self._nested_brackets(level=5))
    self.latex_out = re.sub(env_repl, "", self.latex_out)

    #print("ENV replacements:")

    if env_matches:
      #print(env_matches)
      self.env_replacements = env_matches
      for e in self.env_replacements:
        m = Macro(
          int(e[2]) if e[2] != '' else 0,
          TexMacroExpander.trim_string(e[3]))
        self.macros[TexMacroExpander.trim_string(e[0])] = m

    # Extract all \DeclareMathOperator[*]
    decl_math_matches = re.findall(
      r"\\DeclareMathOperator(\*?) *(" + cs + r"|\{" + cs + r"\}) *" + self._nested_brackets(5), 
      self.latex_in)
    math_repl = re.compile(r"\\DeclareMathOperator(\*?) *(" + cs + r"|\{" + cs + r"\}) *" + self._nested_brackets(5))
    self.latex_out = re.sub(math_repl, "", self.latex_out)
    #print("DeclareMath* replacements:")
    if decl_math_matches:
      #print(decl_math_matches)
      self.math_replacements = decl_math_matches
      for e in self.math_replacements:
        m = Macro(
          0,
          "\\operatorname" + e[0] + "{" + TexMacroExpander.trim_string(e[2]) + "}"
        )
        self.macros[TexMacroExpander.trim_string(e[1])] = m

    #print("="*20)
    #print("Fetched Macros:")
    #for m in self.macros:
    #  print(m)

    #print("Latex_In: {}".format(self.latex_in))

  def _expand_macros(self):
    # Loop through all entries of self.macros and start the replacement
    temp_out = self.latex_out
    for k, v in self.macros.items():
      # Create regex for that
      repl_regex = re.compile(self._create_regex(k, v))
      #print("Generated Regex for {}: {}".format(k, repl_regex))
      num = v.num

      shift = 0

      for x in re.finditer(self._create_regex(k, v), self.latex_out):
        x_group = str(x.group())
        #print("Found: {}".format(x_group))
        #print("-> {}".format(x.span()[0]))
        
        final_repl = v.definition #.replace("\\", "\\\\")
        for k in range(num):
          m = x.group(k+1)
          #print("Fetch argument: {}".format(m))
          final_repl = final_repl.replace("#{}".format(k+1), TexMacroExpander.trim_string(m))
        #print("\tby: {}".format(final_repl))

        #print("-> {}".format(x.group()))


        inc_shift = len(final_repl)- (x.span()[1] - x.span()[0])
        
        self.latex_out = self.latex_out[:x.span()[0]+shift] + final_repl + self.latex_out[x.span()[1]+shift:]

        shift += inc_shift
    
    #self.latex_out = temp_out


  def _nested_brackets(self, level=5):
    reg = r"(?:[^\r\n\{\}]|\\\[\{\}]|\r?\n(?!\r?\n))*?"
    c = r"(?:[^\r\n\{\}]|\\\[\{\}]|\r?\n(?!\r?\n))*?"

    lvl = level

    while lvl > 0:
      reg = c + r"(?:\{" + reg + r"\}" + c + r")*?"
      lvl -= 1
    return r" *(\{" + reg + r"\}|[^\{])"

  @staticmethod
  def trim_string(string):
    return re.sub(r"^\{|\}$", '', re.sub(r"^ +| +$", '', string))

  def _create_regex(self, name, macro):
    num = macro.num
    #repl = macro.definition
    #print("Create regex for : {}".format(name))

    gen_regex_ = r""

    while num > 0:
      gen_regex_ += self._nested_brackets(0)

      num -= 1

    gen_regex_ = r"\\" + name[1:] + r"(?![a-zA-Z\}])" + gen_regex_

    #print("Searching for regex: {}".format(gen_regex_))
    return gen_regex_