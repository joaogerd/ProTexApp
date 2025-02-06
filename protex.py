#!/usr/bin/env python3
# ===================================================================
# ProTeX v2.00 - Translates Code Prologues to LaTeX (Python Version)
# ===================================================================
# 
# Original Perl version by A. da Silva, 1995.
# 
# Revision History (Original Perl Version):
# ------------------------------------------
#   20Dec1995  da Silva  First experimental version.
#   10Nov1996  da Silva  First internal release (v1.01).
#   28Jun1997  da Silva  Modified so that !DESCRIPTION can appear after
#              !INTERFACE, and !INPUT PARAMETERS etc. changed to italics.
#   02Jul1997  Sawyer    Added shut-up mode.
#   20Oct1997  Sawyer    Added support for shell scripts.
#   11Mar1998  Sawyer    Added: file name, date in header, C, script support.
#   05Aug1998  Sawyer    Fixed LPChang-bug-support-for-files-with-underscores.
#   10Oct1998  da Silva  Introduced -f option for removing source file info
#                        from subsection, etc.  Added help (WS).
#   06Dec1999  C. Redder Added LaTeX command "\label{sec:prologues}" just 
#                        after the beginning of the prologue section.
#   13Dec1999  C. Redder Increased flexibility in command-line interface.
#                        The options can appear in any order which will allow
#                        the user to implement options for select files.
#   01Feb1999  C. Redder Added \usepackage commands to preamble of LaTeX
#                        document to include the packages amsmath, epsfig,
#                        and hangcaption.
#   10May2000  C. Redder Revised LaTeX command "\label{sec:prologues}"
#                        to "\label{app:ProLogues}".
#   10/10/2002 da Silva  Introduced ARGUMENTS keyword, touch ups.
#   15Jan2003  R. Staufer Modified table of contents to print only section headers - no descriptions.
#   25Feb2003  R. Staufer Added BOPI/EOPI and -i (internal) switch to provide the option
#                        of omitting prologue information from output files.
# 
# Revision History (Python Version):
# -------------------------------------
#   - Converted and reorganized from the original Perl version to Python.
#   - Added comprehensive documentation and improved command-line parsing.
#   05May2023  J. G. de Mattos  Added Shell script support (Python version).
#   05May2023  J. G. de Mattos  Added Python script support (Python version).
#   01Feb2025  J. G. de Mattos  Added a custon style option
# 
# -----------------------------------------------------------------------
# Command Line Switches:
# -----------------------------------------------------------------------
#   -h   : Help mode: list command line options
#   -b   : Bare mode, meaning no preamble, etc.
#   -i   : Internal mode: omit prologues marked !BOPI
#   +/-n : New page for each subsection (wastes paper)
#   +/-l : Listing mode, default is prologues only
#   +/-s : Shut-up mode, i.e., ignore any code from BOC to EOC
#   +/-x : No LaTeX mode, i.e., put !DESCRIPTION: in verbatim mode
#   +/-f : No source file info
#   -A   : Ada code
#   -C   : C++ code
#   -F   : F90 code (default)
#   -S   : Shell script
# 
# The options can appear in any order. The options -h and -b affect the input from all 
# files listed on the command line.
# Each of the remaining options affects only the input from the files listed after that 
# option and prior to any overriding option.
# The plus sign turns off the option. For example, the command-line:
#     protex -bnS File1 -F File2.f +n File3.f
# will cause the option -n to affect the input from the files File1 and File2.f, but not
# from File3.f.
# The -S option is implemented for File1 but is overridden by -F for File2.f and File3.f.
# 
# -----------------------------------------------------------------------
# See Also:
#   For a more detailed description of ProTeX functionality, DAO Prologue, and other conventions, consult:
#     Sawyer, W., and A. da Silva, 1997: ProTeX: A Sample Fortran 90 Source Code Documentation System.
#     DAO Office Note 97-11.

import sys
import os
import argparse
from datetime import datetime
import textwrap

import argparse

# Centralized mapping: all language-related data in a single dictionary
language_info = {
    'F': {"name": "Fortran90", "comment": '!',    "lang": 'fortran'},  # Default language
    'A': {"name": "Ada",       "comment": '--',   "lang": 'ada'},      
    'C': {"name": "C++",       "comment": '//',   "lang": 'c'},        
    'S': {"name": "Shell",     "comment": '#',    "lang": 'bash'},     
    'G': {"name": "GrADS",     "comment": '*',    "lang": 'bash'},
    'P': {"name": "Python",    "comment": '#',    "lang": 'python'}
}

def get_language_info(code: str, info_type: str = "comment") -> str:
    """
    Retrieves language-related information based on the provided language code.

    This function provides a mapping between a language code and its corresponding:
    - Comment symbol (used in source code)
    - LaTeX Minted language name (for syntax highlighting)
    - Full language name (for display purposes)

    Args:
        code (str): The language code corresponding to a programming or scripting language.
                    Supported codes:
                    - 'F': Fortran90 (default)
                    - 'A': Ada
                    - 'C': C++
                    - 'S': Shell script
                    - 'G': GrADS script
                    - 'P': Python
        info_type (str, optional): The type of information to retrieve. 
                                   Options:
                                   - "comment": Returns the language's comment symbol.
                                   - "lang": Returns the LaTeX Minted language name.
                                   - "name": Returns the full name of the language.
                                   Defaults to "comment".

    Returns:
        str: The requested comment symbol, language name, or LaTeX Minted name.

    Raises:
        ValueError: If an invalid language code is provided.
        ValueError: If an invalid info_type is provided.

    Example Usage:
        >>> get_language_info('F', "comment")
        '!'

        >>> get_language_info('C', "lang")
        'c'

        >>> get_language_info('A', "name")
        'Ada'

        >>> get_language_info('X', "comment")  # Invalid code
        Traceback (most recent call last):
            ...
        ValueError: Invalid language code: 'X'

        >>> get_language_info('F', "invalid_type")
        Traceback (most recent call last):
            ...
        ValueError: Invalid info_type: 'invalid_type', must be 'comment', 'lang' or 'name'
    """
    if code not in language_info:
        raise ValueError(f"Invalid language code: '{code}'")

    if info_type not in ["comment", "lang", "name"]:
        raise ValueError(f"Invalid info_type: '{info_type}', must be 'comment', 'lang' or 'name'")

    return language_info[code][info_type]

#-------------------------------
# Define tokens for each language
#-------------------------------
def get_language_tokens(lang):
    """Returns a dictionary of tokens for the specified language, based solely on the comment symbol.

    Args:
        lang (str): Language code ('F' for Fortran90, 'A' for Ada, 'C' for C++, 'S' for Shell, G for GrADS).

    Returns:
        dict: Dictionary with all token strings generated using the language-specific comment symbol.
    """

    symbol = get_language_info(lang,"comment")
    
    # Build and return the tokens dictionary using the comment symbol.
    return {
        "comment": symbol,
        "bop": symbol + "BOP",
        "eop": symbol + "EOP",
        "boi": symbol + "BOI",
        "eoi": symbol + "EOI",
        "boc": symbol + "BOC",
        "eoc": symbol + "EOC",
        "boe": symbol + "BOE",
        "eoe": symbol + "EOE",
        "bor": symbol + "BOR",
        "eor": symbol + "EOR",
        "bopi": symbol + "BOPI",
        "eopi": symbol + "EOPI",
        "iiro": symbol + "IIROUTINE:",
        "cro": symbol + "CROUTINE:",
        "program": symbol + "PROGRAM:"
    }


#-------------------------------
# LaTeX preamble and macros
#-------------------------------
def print_notice():
    """Prints the notice header in the LaTeX document."""
    print("%                **** IMPORTANT NOTICE *****")
    print("% This LaTeX file was automatically generated by ProTeX (Python version)")
    print("% Any changes made to this file will likely be lost next time")
    print("% it is regenerated from its source. Send questions to joao.gerd@inpe.br\n")


def print_preamble(custom_style=None):
    """Prints the LaTeX preamble.

    If a custom_style is provided, it uses that style; otherwise, it uses the default document class.

    Args:
        custom_style (str, optional): Custom document class or style.
    """
    print("%------------------------ PREAMBLE --------------------------")
    if custom_style:
        print("\\documentclass[11pt]{" + custom_style + "}")
        print("\\usepackage{" + custom_style + "}")
    else:
        print("\\documentclass[11pt]{article}")

    print("\\usepackage{amsmath}")
    print("\\usepackage{epsfig}")
    print("\\usepackage{minted}")

    print("\\textheight     9in")
    print("\\topmargin      0pt")
    print("\\headsep        1cm")
    print("\\headheight     0pt")
    print("\\textwidth      6in")
    print("\\oddsidemargin  0in")
    print("\\evensidemargin 0in")
    print("\\marginparpush  0pt")
    print("\\pagestyle{myheadings}")
    print("\\markboth{}{}")
    print("%-------------------------------------------------------------")
    print("\\setlength{\\parskip}{0pt}")
    print("\\setlength{\\parindent}{0pt}")
    print("\\setlength{\\baselineskip}{11pt}")


def print_macros():
    """Prints LaTeX macros for shorthand commands."""
    print("\n%--------------------- SHORT-HAND MACROS ----------------------")
    print("\\def\\be{\\begin{equation}}")
    print("\\def\\ee{\\end{equation}}")
    print("\\def\\bea{\\begin{eqnarray}}")
    print("\\def\\eea{\\end{eqnarray}}")
    print("\\def\\bi{\\begin{itemize}}")
    print("\\def\\ei{\\end{itemize}}")
    print("\\def\\bn{\\begin{enumerate}}")
    print("\\def\\en{\\end{enumerate}}")
    print("\\def\\bd{\\begin{description}}")
    print("\\def\\ed{\\end{description}}")
    print("\\def\\({\\left (}")
    print("\\def\\){\\right )}")
    print("\\def\\[{\\left [}")
    print("\\def\\]{\\right ]}")
    print("\\def\\<{\\left \\langle}")
    print("\\def\\>{\\right \\rangle}")
    print("\\def\\cI{{\\cal I}}")
    print("\\def\\diag{\\mathop{\\rm diag}}")
    print("\\def\\tr{\\mathop{\\rm tr}}")
    print("%-------------------------------------------------------------")


#-------------------------------
# New: Helper to process resource lines
#-------------------------------
def process_resource_line(line):
    """Processes a resource line by splitting it by commas and printing a LaTeX table row.

    Args:
        line (str): The line to process.

    Returns:
        None
    """
    parts = [p.strip() for p in line.split(',')]
    if len(parts) >= 4:
        print("\\makebox[1.0in][l]{" + parts[0] + "} & " +
              "\\makebox[3.5in][l]{" + parts[1] + "} & " +
              "\\makebox[1.0in][l]{" + parts[2] + "} & " +
              "\\makebox[1.0in][l]{" + parts[3] + "} \\\\")
        print("\\hline")
    else:
        print(line)


#-------------------------------
# Document starting/ending functions
#-------------------------------
def do_beg(state, bare):
    """Begins the LaTeX document by printing title, TOC, etc.

    Args:
        state (dict): Global document state.
        bare (bool): Bare mode flag.
    """
    if bare:
        return
        
    if not state["begdoc"]:
        if state["tpage"]:
            print("\\title{" + state["title"] + "}")
            print("\\author{{\\sc " + state["author"] + "}\\\\ {\\em " + state["affiliation"] + "}}")
            print("\\date{" + state["doc_date"] + "}")

        print("\\begin{document}")
        if state["tpage"]:
            print("\\maketitle")

        print("\\tableofcontents")
        print("\\newpage")

        state["begdoc"] = True

def do_boc(state, lang_name):
    """Begin a verbatim/code block if active.

    Args:
        state (dict): Global document state.
    """
    print("\n %------------------ START CODE ------------------%")
    state["first"]    = False
    state["prologue"] = False
    state["source"]   = True
    state["verb"]     = True
    print(f"\\begin{{minted}}[breaklines,breakafter=-+*/&]{{{lang_name}}}")


def do_eoc(state):
    """Ends a verbatim/code block if active.

    Args:
        state (dict): Global document state.
    """
    if state["verb"]:
        print("\\end{minted}")
        state["verb"] = False
        
    state["source"] = False
    print("\n %------------------ END CODE ------------------%")



def set_missing(state):
    """Resets required prologue markers.

    Args:
        state (dict): Global document state.
    """
    state["have_name"] = False
    state["have_desc"] = False
    state["have_intf"] = False
    state["have_hist"] = False
    state["name_is"] = "UNKNOWN"


#-------------------------------
# Main processing function
#-------------------------------
def get_format(fmt, remove_source):
    """
    Adjusts a LaTeX format string based on the user's option to remove source file references.
    
    This function checks whether the user has opted to remove the '(Source File: %s)' part
    from the LaTeX formatting string. If removal is requested, the function modifies the 
    format string accordingly; otherwise, it returns the original string unchanged.

    Args:
        fmt (str): The original LaTeX format string, which may contain '(Source File: %s)'.
        remove_source (bool): Flag indicating whether to remove the source file reference.

    Returns:
        str: The modified or original format string, depending on the value of `remove_source`.

    Example:
        >>> get_format("\\subsection{Fortran: Module Interface %s (Source File: %s)}\n", True)
        '\\subsection{Fortran: Module Interface %s }\n'
        
        >>> get_format("\\subsubsection{%s (Source File: %s)}\n", False)
        '\\subsubsection{%s (Source File: %s)}\n'
    """
    if remove_source:
        return fmt.replace(" (Source File: %s)", "")
    return fmt

def get_format(fmt, remove_source):
    """
    Adjusts a LaTeX format string based on the user's option to remove source file references.
    
    This function checks whether the user has opted to remove the '(Source File: %s)' part
    from the LaTeX formatting string. If removal is requested, the function modifies the 
    format string accordingly; otherwise, it returns the original string unchanged.

    Args:
        fmt (str): The original LaTeX format string, which may contain '(Source File: %s)'.
        remove_source (bool): Flag indicating whether to remove the source file reference.

    Returns:
        str: The modified or original format string, depending on the value of `remove_source`.

    Example:
        >>> get_format("\\subsection{Fortran: Module Interface %s (Source File: %s)}\n", True)
        '\\subsection{Fortran: Module Interface %s }\n'
        
        >>> get_format("\\subsubsection{%s (Source File: %s)}\n", False)
        '\\subsubsection{%s (Source File: %s)}\n'
    """
    if remove_source:
        return fmt.replace(" (Source File: %s)", "")
    return fmt


def get_prologue_processors(opts):
    """
    Creates a dictionary of processing functions for different Fortran documentation markers.

    This function generates a dictionary where each key corresponds to a specific marker
    used in Fortran source code comments (e.g., "!MODULE:", "!PROGRAM:"). Each value is a 
    function that processes the corresponding marker and generates LaTeX output.

    If the `opts.f` flag is set to `True`, the function removes the source file reference
    from the LaTeX output.

    Args:
        opts (Namespace): Command-line options containing the `f` flag, which determines
                          whether to exclude '(Source File: %s)' from the LaTeX output.

    Returns:
        dict: A dictionary mapping documentation markers to processing functions.

    Example:
        >>> class Opts:
        ...     f = True
        >>> opts = Opts()
        >>> prologue_processors = get_prologue_processors(opts)
        >>> print(prologue_processors["!MODULE:"])  # Function reference

    Notes:
        - The `process_generic` function is used to handle most markers, with the formatting
          adjusted based on the `opts.f` flag.
        - Some markers (e.g., "!IROUTINE:", "!IFUNCTION:") are processed by separate functions
          (`process_internal`, `process_overloaded`, `process_contained`).
    """
    remove_source = getattr(opts, 'f', False)

    return {
        "!MODULE:": lambda fields, fb, opts, state: process_generic(
            fields,
            get_format("\\subsection{Fortran: Module Interface %s (Source File: %s)}\n", remove_source),
            fb, opts, state
        ),
        "!PROGRAM:": lambda fields, fb, opts, state: process_generic(
            fields,
            get_format("\\subsection{Fortran: Main Program %s (Source File: %s)}\n", remove_source),
            fb, opts, state
        ),
        "!ROUTINE:": lambda fields, fb, opts, state: process_generic(
            fields,
            get_format("\\subsubsection{%s (Source File: %s)}\n", remove_source),
            fb, opts, state
        ),
        "!FUNCTION:": lambda fields, fb, opts, state: process_generic(
            fields,
            "\\subsubsection{%s (Source File: %s)}\n",  # Maintains source file reference
            fb, opts, state
        ),
        "!IROUTINE:": process_internal,
        "!IFUNCTION:": process_internal,
        "!IIROUTINE:": process_overloaded,
        "!CROUTINE:": process_contained
    }


def process_generic(fields, latex_template, file_basename, opts, state):
    """Processes a generic prologue marker and prints the corresponding LaTeX output.

    This function concatenates the remaining tokens in `fields` (which represent the content
    after the marker), replaces underscores with "\_", and then formats that content using
    the provided LaTeX template. The template should have two placeholders:
      - The first for the content (e.g., a routine or module name).
      - The second for the source file base name.
    
    Example:
        If fields = ["MyModule"], file_basename = "m_time.f90", and
        latex_template = "\\subsection{Fortran: Module Interface %s (Source File: %s)}\n",
        the function will print:
        
          \subsection{Fortran: Module Interface MyModule (Source File: m\_time.f90)}
    
    Args:
        fields (list of str): Tokens representing the content after the marker.
        latex_template (str): A LaTeX template string with two %s placeholders.
        file_basename (str): The formatted source file name.
        opts (Namespace): Command-line options.
        state (dict): Global document state.
    
    Side Effects:
        Prints the formatted LaTeX output to stdout.
    """
    latex_template = get_format(latex_template, opts.f)
    
    content = " ".join(fields).replace("_", "\\_")
    if opts.n and state.get("not_first", False):
        print("\\newpage")
    if not opts.f:
        print(latex_template % (content, file_basename))
    else:
        # If file info is not to be printed, supply an empty string for the second placeholder.
        print(latex_template % content)
    state["have_name"] = True
    state["not_first"] = True


def process_internal(fields, file_basename, opts, state):
    """Processes an internal routine marker (!IROUTINE:) and prints a LaTeX section.

    This function concatenates the tokens in `fields` (the content after the marker),
    replaces underscores with "\_", and extracts a short label from the second word (if available).
    It then prints a LaTeX subsubsection using the short label as an optional argument.
    
    Example:
        If fields = ["Helper", "Routine"] then the function prints:
        
          \subsubsection [Routine]{Helper Routine}
    
    Args:
        fields (list of str): Tokens representing the content after the marker.
        file_basename (str): The source file base name (not used in this function).
        opts (Namespace): Command-line options.
        state (dict): Global document state.
    
    Side Effects:
        Prints the formatted LaTeX output for an internal routine.
    """
    content = " ".join(fields).replace("_", "\\_")
    words = content.split()
    short_label = words[1] if len(words) > 1 else ""
    print("\\subsubsection [%s]{%s}\n" % (short_label, content))
    state["have_name"] = True


def process_overloaded(fields, file_basename, opts, state):
    """Processes an overloaded routine marker (!IIROUTINE:) and prints a LaTeX section.

    This function handles overloaded routines by concatenating the tokens in `fields`,
    replacing underscores with "\_", and extracting a short label from the subsequent tokens.
    It then prints a LaTeX subsubsection with the short label.
    
    Example:
        If fields = ["Overload", "Variant1"] then the function prints:
        
          \subsubsection [Variant1]{Overload Variant1}
    
    Args:
        fields (list of str): Tokens representing the content after the marker.
        file_basename (str): The source file base name (not used here).
        opts (Namespace): Command-line options.
        state (dict): Global document state.
    
    Side Effects:
        Prints the formatted LaTeX output for an overloaded routine.
    """
    content = " ".join(fields).replace("_", "\\_")
    words = content.split()
    short_label = " ".join(words[1:]) if len(words) > 1 else ""
    print("\\subsubsection [%s]{%s}\n" % (short_label, content))
    state["have_name"] = True


def process_contained(fields, file_basename, opts, state):
    """Processes a contained routine marker (!CROUTINE:) and prints a LaTeX section.

    This function concatenates the tokens in `fields` (the content after the marker),
    replaces underscores with "\_", and extracts a short label from the second word (if available).
    It then prints a LaTeX subsubsection using the extracted label.
    
    Example:
        If fields = ["Contained", "Routine"] then the function prints:
        
          \subsubsection [Routine]{Contained Routine}
    
    Args:
        fields (list of str): Tokens representing the content after the marker.
        file_basename (str): The source file base name (not used here).
        opts (Namespace): Command-line options.
        state (dict): Global document state.
    
    Side Effects:
        Prints the formatted LaTeX output for a contained routine.
    """
    content = " ".join(fields).replace("_", "\\_")
    words = content.split()
    short_label = words[1] if len(words) > 1 else ""
    print("\\subsubsection [%s]{%s}\n" % (short_label, content))
    state["have_name"] = True


def process_file(f, filename, state, tokens, lang, opts):
    """
    Processes a source file and prints LaTeX output based on DAO prologues.
    
    This function reads the source file line by line, determines the type of documentation
    marker, and calls the appropriate processing function. The output is printed as LaTeX commands.

    Args:
        f (file-like object): The open source file.
        filename (str): The name of the file (or '-' for STDIN).
        state (dict): The global state of the document.
        tokens (dict): The dictionary of markup tokens.
        lang (str): Language code ('F' for Fortran90, 'A' for Ada, 'C' for C++, 'S' for Shell, G for GrADS)
        opts (Namespace): Command-line options.

    Side Effects:
        Prints the corresponding LaTeX commands to stdout.
    """
    file_basename = os.path.basename(filename) if filename != '-' else "Standard Input"
    file_basename = file_basename.replace("_", "\\_")
    file_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not (opts.g or opts.M):
        print("\n\\markboth{Left}{Source File: %s,  Date: %s}\n" % (file_basename, file_date))
    
    # Define the dictionary of prologue processors.
    prologue_processors = get_prologue_processors(opts)

    # Get lang name
    lang_name = get_language_info(lang,"lang")

    # Process each line
    for line in f:
        raw_line = line.rstrip("\n").rstrip()  # Remove trailing newline characters and spaces
        line   = raw_line.lstrip() # Remove leading spaces
        fields = line.split(maxsplit=9999)  # Split the string into fields

        # Determine marker index: if the line starts with the comment symbol, then marker is at index 1.
        mi = 0
        if fields and fields[0] == tokens["comment"]:
            mi = 1

        if len(fields) <= mi:
            continue

        # -- Resource Block Processing --
        # If a resource block is active, process lines as resource items.
        if state.get("resource", False):
            if fields[mi] == tokens["eor"]:
                state["resource"] = False
            else:
                process_resource_line(line)
            continue

        # -- Process Global Markers (using fields[mi] for markers in non-prologue sections) --
        # !QUOTE:
        if fields[mi] == '!QUOTE:':
            print(" ".join(fields[mi+1:]))
            continue

        #-------------------------------------------------------------#
        # Introduction start: !BOI
        if fields[mi] == tokens["boi"]:
            state["intro"] = True
            continue
   
        # Process Introduction Data using marker from fields[mi+1]
        if state["intro"] and len(fields) > mi+1:
            marker = fields[mi+1]
            if marker == '!TITLE:':
                if mi == 1: fields.pop(0)
                fields.pop(0)
                state["title"] = " ".join(fields)
                state["tpage"] = True
                continue
            elif marker == '!AUTHORS:':
                if mi == 1: fields.pop(0)
                fields.pop(0)
                state["author"] = " ".join(fields)
                state["tpage"] = True
                continue
            elif marker == '!AFFILIATION:':
                if mi == 1: fields.pop(0)
                fields.pop(0)
                state["affiliation"] = " ".join(fields)
                state["tpage"] = True
                continue
            elif marker == '!DATE:':
                if mi == 1: fields.pop(0)
                fields.pop(0)
                state["doc_date"] = " ".join(fields)
                state["tpage"] = True
                continue
            elif marker == '!INTRODUCTION:':
                do_beg(state, opts.bare)
                print(" %..............................................")
                if mi == 1: fields.pop(0)
                fields.pop(0)
                print("\\section{" + " ".join(fields) + "}")
                continue

        if fields[mi] == tokens["eoi"]:
            print("\n %/////////////////////////////////////////////////////////////")
            print("\\newpage")
            state["intro"] = False
            continue
        # Introduction end: !EOI
        #-------------------------------------------------------------#


        #-------------------------------------------------------------#
        # -------------------- Start of Prologue -------------------- #
        #-------------------------------------------------------------#

        # Resourse start: !BOR
        # Check resource block marker first
        if fields[mi] == tokens["bor"]:
            print("\\begin{center}")
            print("{\\bf RESOURCES:}\\\\")
            print("\\begin{tabular}{|l|l|l|l|}")
            print("\\hline")
            print("\\textbf{Name} & \\textbf{Description} & \\textbf{Units} & \\textbf{Default} \\\\")
            print("\\hline")
            print("\\end{tabular}")
            print("\\end{center}")
            state["resource"] = True
            continue

        # Prologue start: !BOP
        if fields[mi] == tokens["bop"]:
            if state["source"]:
                do_eoc(state)
                
            do_beg(state, opts.bare)

            if not state["first"]:
                print("\n\\mbox{}\\hrulefill\\")
            else:
                if not opts.bare and not (opts.g or opts.M):
                    print("\\section{Routine/Function Prologues} \\label{app:ProLogues}")

            state["first"]    = False
            state["prologue"] = True
            state["verb"]     = False
            state["source"]   = False
            set_missing(state)
            continue

        if fields[mi] == tokens["bopi"]:
            if opts.internal:
                state["prologue"] = False
            else:
                if state["source"]:
                    do_eoc(state)

                do_beg(state, opts.bare)

                if not state["first"]:
                    print("\n\\mbox{}\\hrulefill\\")
                else:
                    if not opts.bare and not (opts.g or opts.M):
                        print("\\section{Routine/Function Prologues} \\label{app:ProLogues}")

                state["first"]    = False
                state["prologue"] = True
                state["verb"]     = False
                state["source"]   = False
                set_missing(state)
            continue

        # For lines in a prologue, use the marker from fields[1] (if available)
        
        # Processing prologue markers in a generic way:
        if state["prologue"]:
            marker = fields[1] if len(fields) > 1 else fields[0]
            if marker in prologue_processors:
                if mi == 1:
                    fields.pop(0)
                fields.pop(0)
                prologue_processors[marker](fields, file_basename, opts, state)
                continue

            # New marker: resource blocks are processed outside of prologue below
            # Process !DESCRIPTION:
            if "!DESCRIPTION:" in line:
                if state["verb"]:
                    print("\\end{minted}")
                    print("{\\sf DESCRIPTION:\\\\ }")
                    print("")
                    state["verb"] = False
                if opts.nolatex:
                    print(f"\\begin{{minted}}[breaklines]{{{lang_name}}}")
                    state["verb"] = True
                else:
                    parts = line.split()
                    start = 1 if parts[0] == '!' else 0
                    print(" ".join(parts[start+1:]))
                state["have_desc"] = True
                continue
            # Process optional keywords
            processed_key = False
            for key in opts.keys:
                if key in line:
                    if state["verb"]:
                        print("\\end{minted}")
                        state["verb"] = False
                    else:
                        print("\n\\bigskip")
                    label = key[1:]
                    if any(x in line for x in ["USES", "INPUT", "OUTPUT", "PARAMETERS", "VALUE", "ARGUMENTS"]):
                        print("{\\em " + label + "}")
                    else:
                        print("{\\sf " + label + "}")

                    print(f"\\begin{{minted}}[breaklines]{{{lang_name}}}")
                    state["verb"] = True
                    processed_key = True
                    break
            if processed_key:
                continue

            # End of prologue markers !EOP or !EOPI:
            if fields[mi] in (tokens["eop"], tokens["eopi"]):
                if state["verb"]:
                    print("\\end{minted}")
                    state["verb"] = False
                state["prologue"] = False
                continue

        # -- Code Block --
        if fields[mi] == tokens["boc"]:
            if opts.s:
                state['prologue'] = False
            else:
                do_boc(state, lang_name)
            continue

        if fields[mi] == tokens["eoc"]:
            do_eoc(state)
            continue

        # -- Example Prologue --
        if fields[mi] == tokens["boe"]:
            if state["source"]:
                do_eoc(state)

            print("\n %/////////////////////////////////////////////////////////////")
            state["first"]    = False
            state["prologue"] = True
            state["verb"]     = False
            state["source"]   = False
            continue

        if fields[mi] == tokens["eoe"]:
            if state["verb"]:
                print("\\end{minted}")
                state["verb"] = False

            state["prologue"] = False
            continue

        # If in prologue or introduction, print the line (removing the initial comment symbol)
        if state["prologue"] or state["intro"]:
            if line.startswith(tokens["comment"]):
                line = line[len(tokens["comment"]):]
            print(line)
            continue

        # If in source code section, print the line as-is.
        if state["source"]:
            print(raw_line)
            continue

    # End of file processing
    print("")
    if state["source"]:
        do_eoc(state)


def main():
    """Main function that parses command-line arguments and generates the LaTeX documentation.

    Reads the command-line options, sets up the appropriate tokens based on the source language,
    initializes the global state, and processes each file to generate LaTeX output.
    """
    parser = argparse.ArgumentParser(
        description="ProTeX - Processes Code Prologues into LaTeX (Python version)"
    )
    parser.add_argument("files", nargs="*", help="Source files (use '-' for STDIN)")
    parser.add_argument("-b", "--bare", action="store_true", help="Bare mode: no preamble")
    parser.add_argument("-g", action="store_true", help="Use GEOS style")
    parser.add_argument("-M", action="store_true", help="Use MAPL style")
    parser.add_argument("--n", action="store_true", help="New page for each subsection")
    parser.add_argument("--l", action="store_true", help="Listing mode (only prologues)")
    parser.add_argument("--s", action="store_true", help="Shut-up mode (ignore code between BOC and EOC)")
    parser.add_argument("--x", dest="nolatex", action="store_true", help="No LaTeX mode (print !DESCRIPTION in verbatim)")
    parser.add_argument("--f", action="store_true", help="Do not display source file info")
    parser.add_argument("--i", dest="internal", action="store_true", help="Internal mode: omit prologues !BOPI/EOPI")
    parser.add_argument("--keys", nargs="*", default=[
        "!INTERFACE:", "!USES:", "!PUBLIC TYPES:", "!PRIVATE TYPES:",
        "!PUBLIC MEMBER FUNCTIONS:", "!PRIVATE MEMBER FUNCTIONS:",
        "!PUBLIC DATA MEMBERS:", "!PARAMETERS:", "!ARGUMENTS:",
        "!DEFINED PARAMETERS:", "!INPUT PARAMETERS:", "!INPUT/OUTPUT PARAMETERS:",
        "!OUTPUT PARAMETERS:", "!RETURN VALUE:", "!REVISION HISTORY:",
        "!BUGS:", "!SEE ALSO:", "!SYSTEM ROUTINES:", "!FILES USED:",
        "!REMARKS:", "!TO DO:", "!CALLING SEQUENCE:", "!AUTHOR:",
        "!CALLED FROM:", "!LOCAL VARIABLES:"
    ], help="List of optional keyword markers")
    parser.add_argument("--style", type=str, default=None,
                        help="Custom LaTeX document class or style to use (e.g., 'myStyle')")

    # Creating the argument parser dynamically based on the language_info dictionary
    for code, details in language_info.items():
        parser.add_argument(f"-{code}", action="store_true", help=f"{details['name']} code")

    # Parsing command-line arguments
    opts = parser.parse_args()

    # Determining the selected language
    lang = next((code for code in language_info if getattr(opts, code)), 'F')  # Default: Fortran

    tokens = get_language_tokens(lang)
    global comment_string
    comment_string = tokens["comment"]

    # Determine if GEOS/MAPL style is active
    is_mapl = opts.g or opts.M

    # Global state of the document
    state = {
        "intro":     False,
        "prologue":  False,
        "first":     True,
        "source":    False,
        "verb":      False,
        "tpage":     False,
        "begdoc":    False,
        "not_first": False,
        "have_name": False,
        "have_desc": False,
        "have_intf": False,
        "have_hist": False,
        "name_is":   "UNKNOWN",
        "title": "",
        "author": "",
        "affiliation": "",
        "doc_date": "",
        "resource": False  # New flag for resource block
    }

    files = opts.files if opts.files else ['-']

    print_notice()
    if not opts.bare:
        print_preamble(opts.style)
    print_macros()

    for filename in files:
        if filename == '-' or filename == '':
            process_file(sys.stdin, filename, state, tokens, lang, opts)
        else:
            with open(filename, 'r') as f:
                process_file(f, filename, state, tokens, lang, opts)
    
    if not opts.bare:
        print("\\end{document}")


if __name__ == "__main__":
    main()

