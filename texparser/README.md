# TexParser

As the name suggests a LateX parser, improving on the implementation of pylatexenc [0].

## Installation

```
python -m setup install --user
```

## Usage

There are in general three different console scripts which can be used:

 * texwalker

   This script resolves and prints the node structure of a tex file.
 * tex2text

   This script will print the tex as raw text file.
 * texsimplifier
 
   This script simplifies the tex given tex file, defined structures will be either kept
   or removed from the resulting tex document.

## Sources

[0] https://github.com/phfaist/pylatexenc