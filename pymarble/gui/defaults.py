""" default strings, default json objects """

defaultConfiguration = {
  "lastDirectory": "",
  "columns": ["start", "length", "key", "value"],
}
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
