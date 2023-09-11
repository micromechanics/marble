[![Pylint](https://github.com/micromechanics/marble/actions/workflows/pylint.yml/badge.svg)](https://github.com/micromechanics/marble/actions/workflows/pylint.yml)
[![MyPy](https://github.com/micromechanics/marble/actions/workflows/mypy.yml/badge.svg)](https://github.com/micromechanics/marble/actions/workflows/mypy.yml)
[![pypi](https://github.com/micromechanics/marble/actions/workflows/pypi.yml/badge.svg)](https://github.com/micromechanics/marble/actions/workflows/pypi.yml)
[![coverage](https://codecov.io/gh/micromechanics/marble/graph/badge.svg?token=3Z5TL6SG1H)](https://codecov.io/gh/micromechanics/marble)

# Documentation on software for deciphering proprietary binary data-files
Scientific instruments produce proprietary binary data that contains a multitude of primary and metadata. This project aims to create a software that supports the domain scientist in deciphering this data and metadata and supply python scripts that decipher the instrument measurements.

MARBLE is open und free software and can be found at a [Repository](https://github.com/micromechanics/marble) and [Documentation](https://micromechanics.github.io/marble/).

## Contributors
- Steffen Brinckmann (IEK-2, FZJ) [Principal investigator]
- Volker Hofmann (IAS-9 and HMC, FZJ)
- Fiona D.Mello (IAS-9 and HMC, FZJ)

## Introduction into proprietary binary data-files and MARBLE

In  proprietary binary files, data can be grouped sequentially in **sections** - like sequential chapters in a book, and can have very different lengths. The **sections** can have very different lengths: some section only contains the name of the operator while another section contains thousands of temperature values. These files are called **binary** because they are not human readable but are a list of 1s and 0s and they are called **proprietary** because the instrument vendor has designed them particularly for this company or even instrument. As such, these files cannot be deciphered manually and MARBLE supports the scientist in this task.

MARBLE reads the proprietary binary files and - with the help of the scientist - outputs a **python converter**. This python converter can then be used to translate all proprietary binary files from this instrument into an hdf5-file format, which can be easily read by any computer language. The python converter also acts as verification tool: if a binary file A can be converted by this specific converter, then this file A comes from this instrument. This verification ability is helpful in finding files from a particular instrument.

In MARBLE, data in proprietary binary files is grouped into classes:
- **Metadata** is data that describes the experiment. Examples are the name of the operator, the instrument vendor, the start time of the experiment. This metadata is commonly stored in **key-value-pairs**. For instance, "operator" is the key and "Peter Smith" is the value as both form an inseparable pair. Generally, the first parts of proprietary binary files contain lots of metadata.
- **Primary** data is the data that the operator wanted to measure and this primary data has a form of a list. Lets say we want to measure the temperature at our house every 1min and store this information; then temperature is a primary data and stored in a long list. Generally, the instrument also saves the time increment after the measurement start and stores these time increments in a separate list, which is also primary data. Primary data can be of two types floating point numbers with normal or high precision.
- **Undefined** sections are those sections of the file which the scientist and MARBLE have not identified yet. Some of these sections might be important or unimportant. Unimportant sections are those where the programmer at the instrument vendor was lazy and did included garbage or empty space. These might also be linked to specific languages the instrument vendor used for programming.

MARBLE is semi-automatically deciphering files because it has different methods to automatically identify sections in binary files. For some files, the methods work perfectly while for other files they fail. These failures are where the scientist uses his domain knowledge to augment the automatic methods or corrects MARBLE's mistakes:
- The scientist always labels data:
  - specifies the key for a value: if he/she reads a name, the key would be "operator"
  - specifies the **terms**, **units** and **IRI: links to terminology servers**
- Especially primary data has often to be corrected by shifting the starting position or by changing the length. Although these changes feel strange at first, it becomes easier soon after understanding the rule: **"different primary data sections generally have the same length"**.
- The user identifies which sections are **important** as these should be saved in the output. Additionally, the user defines how certain he/she is about specific sections.
- The user can also remove wrongly identified sections and then use other algorithms to identify those.

## How to install and run MARBLE
Install MARBLE with
``` bash
pip install pymarble
```

To start graphical user interface (GUI)
``` bash
marbleGUI
```

## How to use the GUI
1. A dialog opens asking you for a binary file to load.
1. One row will be automatically filled: everything of the file is unknown. Right-click and select "Automatically identify" depending on your data. A lot will be marked in most cases: click the F5 key to only focus on the non-binary data (see also statusbar).
1. Now go through the sections and label them
   - by entering a "key" and "unit" where applicable. You can do that directly in the table columns that are grey: click to enter the key, value, probability, importance.
   - if you double click on the start and length column a form will open which gives you more options
   - If you want that the converter uses certain data, ensure that the "important" checkbox is ticked.
   - For keeping track of your own progress, you can use the "certainty". If you are unsure use red, medium-sure is yellow and very sure is green.
1. Intermediate saving and reloading can be done with the .tags file. Use the F4 and F2 key for convenience.
1. Once you are done, click the save to save a python converter into the directory of the proprietary binary file that you analysed.
1. Go into the directory and use python converter to convert all files from this instrument by executing the command "python <converter.py> <proprietary_binary_file.dat>". You can add the "-v" option to the command to make the converter more verbose during translation. If all the conversions are successful, you deciphered this proprietary binary file successfully.

## How to use the command line interface (CLI)
The CLI allows you to learn more about proprietary binary files and MARBLE. If you want to become more advanced, follow the tutorials in this section.
``` bash
marbleCLI
```
There is a number of tutorials for the CLI:
- [Tensile machine](https://raw.githubusercontent.com/micromechanics/marble/main/tests/tutorial_05mvl.sh)
- [Tensile machine, large file](https://raw.githubusercontent.com/micromechanics/marble/main/tests/tutorial_08mvl.sh)
- [Image data](https://raw.githubusercontent.com/micromechanics/marble/main/tests/tutorial_emi.sh)
- [Data of multiple tests in one file](https://raw.githubusercontent.com/micromechanics/marble/main/tests/tutorial_idr.sh)
- [Tensile machine from above but larger file, that coincidentally requires more understanding](https://raw.githubusercontent.com/micromechanics/marble/main/tests/tutorial_08mvl.sh)

You can read them and follow those commands. However, you can also just execute them with the argument "m", without the quotation marks.
All of these tutorials are in the form of linux scripts, which are used for verification of the code at each development step.
