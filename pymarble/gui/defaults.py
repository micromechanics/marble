""" default strings, default json objects """

defaultConfiguration = {
  "lastDirectory": "",
  "columns": ["start", "length", "key", "value"],
  "optFind": {"maxError":1e-4},
  "optAutomatic": {"minChars":10,   "minArray": 50, "maxExp":11, "minZeros":16, "minEntropy":3},
  "optEntropy": {"blockSize":256, "skipEvery":5}
}
# the opt...: properties are the same as in file.py
#
# additional options
# advanced: anything: e.g. true
# print_mode hex

# "#e5e5e5"  light grey
# "#cccccc" medium grey
# "#e5fdff"  light cyan
# "#65aeb5"  darker cyan
# #eaeafe"  #light blue
# #877bd1"  darker blue
# #9a031e  dark read
dClass2Color = {
  "metadata":"#e5fdff",
  "primary" :"#eaeafe",
  "":        "#f1f1f1",
  "count":   "#cccccc"
}


translatePlot     = {'f':'plot numerical value','d':'plot numerical value','b':'plot byte value',\
                          'B':'plot byte value','c':'plot byte value', 'i':'print numerical value',
                          'H':'2D graph of numerical value'}
translateDtype    = {'b':'byte = 1byte = 8bit', 'c':'character = 1byte',
                     'H':'unsigned short = 2byte = 16bit', 'i':'int = 4bytes',
                     'f':'float = 4bytes','d':'double = 8bytes',}
translateDtypeInv = {v: k for k, v in translateDtype.items()}
translateDtypeShort = {'b':'byte', 'B':'zeros', 'c':'character', 'H':'unsigned short int', 'h':'short int',
                       'i':'int',  'f':'float', 'd':'double'}



ABOUT_TEXT = """
<h3>MARBLE for python</h3>
Scientific instruments produce proprietary binary data that contains a multitude of primary and metadata.
This project aims to create a software that supports the domain scientist in deciphering this data and
metadata and supply python scripts that decipher the instrument measurements.
<br><br>
MARBLE is open software and can be found at a <a href='https://pypi.org/project/pymarble/'>Repository</a>.
<br><br>
Contributors
<ul>
<li> Steffen Brinckmann (IEK-2, FZJ) [Principal investigator]
<li> Volker Hofmann (IAS-9 and HMC, FZJ)
<li> Fiona D.Mello (IAS-9 and HMC, FZJ)
<li> Thomas D&uuml;ren (IEK-2, FZJ)
</ul>
<br>
The project was supported by HMC and FZJ in 2022 and 2021.
"""

INFO_EXPORTED_FILE = """
Use a format that is readable by the default of np.loadtxt<br><br>
Example:<br>
<tt>
#time temperature<br>
0.1   21.2<br>
0.2   25.3<br>
...
</tt>
"""

WARNING_LARGE_DATA = """
<h3>Section has too much data</h3>
<p>
This much data results in problems plotting and printing. If one would choose to plot/print, it will take ages.
Therefore, only $max_plot$ points are plotted and $max_print$ points are printed. This down scaling implies
that only every $scale$ point is plotted / printed, respectively.
</p>
How to use marble:
<ul>
<li> Reduce the length to something appropriate and focus on the start: find the real start
<li> With reduced length: move start up to focus on the end
<li> Use math and remember the byte-size
</ul>
Never plot the entropy.
"""

HELP_PERIODICITY = """
<h3>Important information for periodicity tool</h3>
Please ensure that in the table has the following properties before saving to python file:
<p>
All sections in the first period have to have "important" checked and the last section of this period has to
have a non-binary dType (set it to character if in doubt).
</p>
<p>
All other sections in the following periods have to have "important" unchecked, irrespective of dType.
</p>
"""
