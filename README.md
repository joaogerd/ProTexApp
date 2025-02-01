# ProTeX - Python Version

ProTeX is a Python tool that processes documentation comments embedded in source files (e.g., Fortran code) and generates a formatted LaTeX document. This project is a conversion and reorganization of the original ProTeX (written in Perl by A. da Silva in 1995) to Python, preserving the original functionality and revision history.

> **Note:**  
> This version maintains the original revision history and command‑line switch details from the Perl version while adding improvements and full documentation in Python.

---

## Table of Contents

- [Installation and Execution](#installation-and-execution)
- [Command-Line Options](#command-line-options)
- [Documentation Markers and Their Meanings](#documentation-markers-and-their-meanings)
  - [Section Markers](#section-markers)
  - [Content-Specific Markers](#content-specific-markers)
- [Examples of Use](#examples-of-use)
  - [Example: Header and Introduction](#example-header-and-introduction)
  - [Example: Module Documentation](#example-module-documentation)
  - [Example: Public Routine Documentation](#example-public-routine-documentation)
  - [Example: Internal Routine Documentation](#example-internal-routine-documentation)
  - [Example: Code Block](#example-code-block)
- [Customization and Considerations](#customization-and-considerations)
- [Contributing](#contributing)
- [License](#license)

---

## Installation and Execution

### Prerequisites

- **Python 3.x**  
  Make sure you have Python 3 installed on your system.

### Installation

1. **Clone or Download the Repository:**  
   Place the `protex.py` file in your desired directory.

2. **Make it Executable (Optional):**

   ```bash
   chmod +x protex.py
   ```

### Execution

To generate a LaTeX document from a source file (e.g., `m_time.f90`), run:

```bash
./protex.py -F m_time.f90 > document.tex
```

Alternatively, you can use:

```bash
python3 protex.py -F m_time.f90 > document.tex
```

After generating `document.tex`, compile it with your LaTeX compiler (e.g., using `pdflatex`):

```bash
pdflatex document.tex
```

---

## Command-Line Options

ProTeX accepts various options to customize the output. Below are the main options:

- **`-b`, `--bare`**  
  *Bare mode*: Do not print the preamble or standard elements (useful for embedding the output in a larger document).

- **`-A`**  
  Indicates that the source code is in **Ada**. (The markers will adjust accordingly, using `--` instead of `!`.)

- **`-C`**  
  Indicates that the source code is in **C++**. (The markers will adjust accordingly, using `//`.)

- **`-F`**  
  Indicates that the source code is in **Fortran90** (default). If no language option is specified, Fortran is assumed.

- **`-S`**  
  Indicates that the source code is from a **Shell script**. (Uses `#` as the comment character.)

- **`--n`**  
  Inserts a new page for each subsection.

- **`--l`**  
  *Listing mode*: Only the prologues are printed (useful for generating listings without source code).

- **`--s`**  
  *Shut-up mode*: Ignores the code between code block markers (i.e., between `!BOC` and `!EOC`).

- **`--x`**  
  *No LaTeX mode*: In some blocks (e.g., `!DESCRIPTION:`), the content is printed in verbatim mode instead of being processed as LaTeX.

- **`--f`**  
  Do not display the source file information (e.g., the file name).

- **`--i`**  
  *Internal mode*: Omits prologues marked with `!BOPI/EOPI` (for internal routines).

- **`--keys`**  
  Allows you to specify a custom list of optional keyword markers (e.g., `!INTERFACE:`, `!REVISION HISTORY:`) that will be specially formatted in the document.

---

## Documentation Markers and Their Meanings

ProTeX uses a convention based on specific keywords inserted in the source code comments. The markers are used to separate different sections of documentation.

### Section Markers

- **`!BOI`**  
  Marks the beginning of the **Introduction**. Everything following this marker (until `!EOI`) is considered part of the introduction.

- **`!EOI`**  
  Marks the end of the **Introduction**.

- **`!BOP`**  
  Marks the beginning of a **Prologue** for a routine, function, or module. This block typically contains documentation for the public interface.

- **`!EOP`**  
  Marks the end of the **Prologue**.

- **`!BOPI`**  
  Marks the beginning of an **Internal Prologue** (for internal or auxiliary routines). This block may be omitted if the internal mode (`--i`) is used.

- **`!EOPI`**  
  Marks the end of the **Internal Prologue**.

- **`!BOC`**  
  Marks the beginning of a **Code Block**. The content between `!BOC` and `!EOC` is treated as source code (usually printed verbatim).

- **`!EOC`**  
  Marks the end of a **Code Block**.

- **`!BOE`**  
  Marks the beginning of an **Example Prologue** (for example usage).

- **`!EOE`**  
  Marks the end of an **Example Prologue**.

### Content-Specific Markers

These markers are used inside a prologue block to provide specific information:

- **`!MODULE:`**  
  Used to document a module. The line typically includes the module name.  
  *Example:*  
  ```fortran
  ! !MODULE: m_time.f90
  ```

- **`!ROUTINE:`**  
  Indicates the start of documentation for a public routine or function. The routine's name is provided after the marker.  
  *Example:*  
  ```fortran
  ! !ROUTINE: compute_hours
  ```

- **`!IROUTINE:`**  
  Indicates the start of documentation for an internal routine. The output in LaTeX can include a short label (taken from the second term, if present) for cross-referencing.  
  *Example:*  
  ```fortran
  ! !IROUTINE: internal_helper
  ```

- **`!DESCRIPTION:`**  
  Provides a detailed description of the routine, function, or module.  
  *Example:*  
  ```fortran
  ! !DESCRIPTION: This function calculates the total number of hours between two dates.
  ```

- **Optional Metadata Markers:**  
  These include (but are not limited to):
  - **`!INTERFACE:`** – Specifies the interface of the routine (parameters, types, etc.).
  - **`!REVISION HISTORY:`** – Lists modifications and version history.
  - **`!ARGUMENTS:`** or **`!PARAMETERS:`** – Describes input and output parameters.
  - **`!BUGS:`** – Lists known issues.
  - **`!SEE ALSO:`** – References to related routines or modules.

---

## Examples of Use

Below are some practical examples demonstrating how to document your source code using ProTeX markers.

### Example: Header and Introduction

```fortran
!-----------------------------------------------------------------------------!
!           Group on Data Assimilation Development - GDAD/CPTEC/INPE          !
!-----------------------------------------------------------------------------!
!BOI
! !TITLE: Time Manipulation Module Documentation
! !AUTHORS: John Doe
! !AFFILIATION: CPTEC/INPE - Meteorological Research Group
! !DATE: 2025-02-01
! !INTRODUCTION: This document describes the module that handles time 
!                manipulations such as converting dates, calculating durations,
!                and more.
!EOI
```

**Explanation:**  
This introduction uses `!BOI` to start and `!EOI` to end the introduction. It includes the title, authors, affiliation, date, and a brief overview.

### Example: Module Documentation

```fortran
!BOP
! !MODULE: m_time.f90
! !DESCRIPTION: This module contains routines and functions to manipulate time
!              periods (e.g., converting between Julian and Gregorian dates, calculating
!              total hours, days, months, and years between two dates).
!
! !INTERFACE:
!
MODULE time_module
  IMPLICIT NONE
  PRIVATE
! !PUBLIC MEMBER FUNCTIONS:
  PUBLIC  :: cal2jul, jul2cal, eom, noh, nod, nom, noy
! !REVISION HISTORY:
! 15 Jun 2005 - J. G. de Mattos - Initial version.
! 18 Mar 2010 - J. G. de Mattos - Updated time calculation routines.
! 23 Mar 2010 - J. G. de Mattos - Modified interface for jul2cal.
! !SEE ALSO:
!  Related modules: date_utils.f90, calendar.f90
!EOP
```

**Explanation:**  
This section starts with `!BOP` to begin the prologue for the module. It includes the module name, description, interface details (listing public functions), revision history, and related modules. The block ends with `!EOP`.

### Example: Public Routine Documentation

```fortran
!BOP
! !ROUTINE: compute_hours
! !DESCRIPTION: This function calculates the total number of hours between two dates.
! !INTERFACE: INTEGER FUNCTION compute_hours(start_date, end_date)
! !ARGUMENTS:
!    start_date - INTEGER: starting date in yyyymmdd format
!    end_date   - INTEGER: ending date in yyyymmdd format
! !RETURN VALUE: INTEGER - Total hours between the two dates.
! !REVISION HISTORY:
!    18 Mar 2010 - Initial version.
!EOP
FUNCTION compute_hours(start_date, end_date) RESULT(total_hours)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: start_date, end_date
  INTEGER :: total_hours
  ! Implementation code goes here...
END FUNCTION compute_hours
```

**Explanation:**  
The marker `!ROUTINE:` is used for a public routine. The documentation includes a detailed description, interface signature, arguments, return value, and revision history.

### Example: Internal Routine Documentation

```fortran
!BOP
! !IROUTINE: internal_helper
! !DESCRIPTION: This internal function assists in converting a date to the Julian day.
! !INTERFACE: INTEGER FUNCTION internal_helper(date)
! !ARGUMENTS:
!    date - INTEGER: date in yyyymmdd format
! !REVISION HISTORY:
!    15 Jun 2005 - Initial version.
!EOP
FUNCTION internal_helper(date) RESULT(julian_day)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: date
  INTEGER :: julian_day
  ! Implementation code goes here...
END FUNCTION internal_helper
```

**Explanation:**  
`!IROUTINE:` marks an internal routine. The output in LaTeX may include a short label. This block is similar to public routines but intended for internal use.

### Example: Code Block

```fortran
!BOC
  DO i = 1, 10
      PRINT *, "Iteration: ", i
  END DO
!EOC
```

**Explanation:**  
The block between `!BOC` and `!EOC` is treated as source code and is typically printed in a verbatim environment, preserving the original formatting.

---

## Customization and Considerations

- **Customizing Keyword Markers:**  
  You can modify the list of optional keyword markers (e.g., `!INTERFACE:`, `!REVISION HISTORY:`) using the `--keys` command-line option.

- **Bare Mode:**  
  If you use the bare mode (`-b`), ProTeX will not print the preamble or other standard document elements. This is useful if you want to embed the output into a larger LaTeX document.

- **Internal Mode:**  
  With the `--i` option, blocks marked with `!BOPI/EOPI` (internal routines) will be omitted from the generated documentation.

- **Language Options:**  
  The options `-A`, `-C`, and `-S` adjust the comment tokens based on the source language (Ada, C++, and Shell, respectively).

---

## Contributing

Contributions are welcome! If you have ideas for improvements, bug fixes, or new features, please open an issue or submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).
