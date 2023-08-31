""" written by Raphael: look up terminology servers """
import json
import requests
from PySide6.QtWidgets import QLabel, QHBoxLayout, QDialogButtonBox, QDialog, QWidget, QVBoxLayout, \
                              QScrollArea, QCheckBox                        # pylint: disable=no-name-in-module
from PySide6.QtCore import QSize, Qt, QByteArray                            # pylint: disable=no-name-in-module
from PySide6.QtGui import QPixmap                                           # pylint: disable=no-name-in-module

class TerminologyLookup(QDialog):
  """ written by Raphael: look up terminology servers """
  def __init__(self, searchterm:str):
    """
    Opens a Dialog which displays definitions for the given searchterm
        and returns chosen definitions as a list

    Args:
        searchterm (str): The term you search for
    """
    super().__init__()

    #variables
    self.listCB:list[tuple[QCheckBox,str]] = []
    self.nested_widgets:list[QWidget]      = []
    self.search_term                       = searchterm
    self.returnValues:list[str]            = []

    #icons
    # pylint: disable=line-too-long
    baWikipedia = QByteArray.fromBase64(b'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')
    baWikidata  = QByteArray.fromBase64(b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAZCAYAAABQDyyRAAABhWlDQ1BJQ0MgUHJvZmlsZQAAeJx9kT1Iw0AcxV/TSotUHewgIpihOlnwC3HUKhShQqgVWnUwufRDaNKQtLg4Cq4FBz8Wqw4uzro6uAqC4AeIq4uToouU+L+k0CLGg+N+vLv3uHsHCPUS06zAKKDpFTOViIuZ7IoYfEUIg+hGAGMys4xZSUrCc3zdw8fXuxjP8j735+hScxYDfCLxDDPMCvE68dRmxeC8TxxhRVklPiceMemCxI9cV1x+41xwWOCZETOdmiOOEIuFNlbamBVNjXiSOKpqOuULGZdVzluctVKVNe/JXxjO6ctLXKc5gAQWsAgJIhRUsYESKojRqpNiIUX7cQ9/v+OXyKWQawOMHPMoQ4Ps+MH/4He3Vn5i3E0Kx4GOF9v+GAKCu0CjZtvfx7bdOAH8z8CV3vKX68D0J+m1lhY9Anq2gYvrlqbsAZc7QN+TIZuyI/lpCvk88H5G35QFem+BzlW3t+Y+Th+ANHWVvAEODoHhAmWvebw71N7bv2ea/f0AerByqoG+UVwAAAOiSURBVHic7ZZPaF1FFIe/MzPv3ibR2L4a0xdioqtaChVUKkJF60IQBKXtxhatgggFsSBawaXgQlAXbtSqC62ripViK6It/SO2KmZhFqVCwCQ++l6bmJrE5N07d2aOi6RVXHSnbvLbnZkzc745M4c58D9LAF7NsttCjOtdjGeCtfcnVWtFQndX18mFTuceUe0R0Omb+77/eO+W2/PKnK/U3+K67cTUZ5vryRbDAMbYiaCyaNGbjDXtGKqNJKOCmR1+qDkyrxfvq0r5Icv1jq5ud3bi2U/aDsCH8GhM6UVgm4/xoANKCFIUW6sY33PQL0BM1VN/VOUbHR9fU0lP5qU5EDqdu6nZRwCS+kOoNqPwQLLmC01uH5og+l8WiuLpBVMcTKQnylLeVrp2AF+65UyEpZgkhTJA/g8bAUQkKloKhKR4RQJoRQrL22gFBBQPBFIATaCUoEk1eVSjipRLE2D+/Vu+tlYAVgBWAFYAVgBWAAyAgNWlH9AAuQX+bjvAAapqgVxFLJCpYIEaxoFxoFpbds0Ad3UcMhCDSEYSi5KDGJadAcYFTjm4XMGxBJmBjhH5XeB0XOoH1GEvGLEnnehEFD1rRcYR04WGNUvHsaMYmSKlbjGMaQynUQUjE1Z0xqocV6stxJywwm//UZKvLQHYtGlTz/z8/N6iKPZnWbYjpfSjtbYHGEoivRG+qalu9d4fcs7tzrLsaAjh3hDCiVqt9ngMwfiq+rzdbp9qNBpDeV57JoT0pjNmF8YMi6iTKr5fiTSs2A3jk+NvXQFwAKOjo8W6deseBjpFUbwsIoe996tF5AywO6V0OYg8LyI7vffHO53OvLX2OWCmqqrHjDGvq+pHAwMDD8YYdxaFf0FVW171vIjsA46o6qIx5hWvfkOj0fiq1Wqdh7+qIAIfAi+JyHfAZmAD8CmAiASgB9ioqnMxxo6qVstrL4YQPgA6McYtIrJLVUdFZM+lS5eOAeMictgYsx64VUSmY4x7rmTgahl6748Ai6r6LnBORL5tt9uTwJSqFiLyk4hsA7Y75+4CflXVWRG5wTl3VES+FpFcVX9W1f3AfH9//1YRubAcZ7uqHgDeMcbcOTw8vPrqG7iioaGhNZOTk7N9fX3deZ7HZrPZGRwcrK9atWqhKIqeZrM5Mzg4WLfWJlWVLMsW5+bmVquqTE1Ntev1em+9Xi/HxsbKtWvXXg+QUjK9vb2l9/66Vqs1DdBoNG4cGBiYHRkZqf4EvLDZAwMOak4AAAAASUVORK5CYII=')
    baOLS = QByteArray.fromBase64(b'iVBORw0KGgoAAAANSUhEUgAAACAAAAANCAYAAADISGwcAAABhWlDQ1BJQ0MgUHJvZmlsZQAAeJx9kT1Iw0AcxV/TSotUHewgIpihOlnwC3HUKhShQqgVWnUwufRDaNKQtLg4Cq4FBz8Wqw4uzro6uAqC4AeIq4uToouU+L+k0CLGg+N+vLv3uHsHCPUS06zAKKDpFTOViIuZ7IoYfEUIg+hGAGMys4xZSUrCc3zdw8fXuxjP8j735+hScxYDfCLxDDPMCvE68dRmxeC8TxxhRVklPiceMemCxI9cV1x+41xwWOCZETOdmiOOEIuFNlbamBVNjXiSOKpqOuULGZdVzluctVKVNe/JXxjO6ctLXKc5gAQWsAgJIhRUsYESKojRqpNiIUX7cQ9/v+OXyKWQawOMHPMoQ4Ps+MH/4He3Vn5i3E0Kx4GOF9v+GAKCu0CjZtvfx7bdOAH8z8CV3vKX68D0J+m1lhY9Anq2gYvrlqbsAZc7QN+TIZuyI/lpCvk88H5G35QFem+BzlW3t+Y+Th+ANHWVvAEODoHhAmWvebw71N7bv2ea/f0AerByqoG+UVwAAAPgSURBVHicdZFbiJV1FMV/e3/371xmjpoXvHSDNFB80HQiLUTo4kuKGGURZBAUZZmYkZnog6iF3UgqrIiQhJKhh0wsirCH0ehFKBhJo0R0jLHjeGbO7fv+u4ej2MzQetuw9tpr7SWMwpabIVsBTAE3E6wBegW8PggPw/bGde6r8yC7B6QN5kHzE3izzji8Mg1sLWSzgQhoQ9AP9g0M9stVllDedh8te6AzSRtogQsRHSLLbyDw6gT+e1S3/glAvHUpsAahhUkXDdkA22ujbpe33Ermb8BZGwDFx1neMSwCHPABmLH7brL8fgqaYyZ4GgHdgI8RYNYEa4G8ROWtHfzxwgCV+KqOAxMjL8HfY8IXyk9gDKFuAkiBnCE8KgiXcVzifP1nnwUfdDEyvBKiEbAYIaSdHcbJScSFiC7HD3rAVYEmuIdh27tUCoYzB+YAhzLawJydE5EwxcyBhDh3gFMbj3DjnqkkwUZy9yW8nPl4LKNcGMFQxLpo2Gv89vS5/0idZtG+3xFdh9lZRKdzZzwJPIdDMRRMSSaMST8xIxAHrgEygHIXUz7+lWPrzgKbrtF8upP5iHgYCdhPHH/8HGNx4pnvufezB8HKwCAiszEdgcw6HYjRHLNzS6VGtWkIZ3A2B9EYs82sOHgByY/y9aMnOgYKSQnIUcqYnB13/BqK0WXQWYAC8xGrQhgDAc5CJnfZKP4XD+WsOrQXyZ9FdYDMdaHqIRLhvLWsOdQD+ftKMa5TiEZIoiKFoPK/BgpxRCG4RCHMKIanSJIzpHGDNB6mGLdohjJup3f1eaYXdxD45ygnSjH2icM6xbhK6N9EFK9Q0vA0aeQoxH+RJkvY9oM/TuipowtJo27SqEYSNSiWTpJ6RhoKSSikEVRKY0uA5/rKXKgZn688SGw78f0jFCMhCRoUkyppuEhYf2wWuOcxFyOagTTR6FO6Rk5DSRlqLCZvPwZSB6thcoUJtptBW4ynqzFrgXSD/y2eG8bU4cx4Z+l3rP9xM0aGuv28vawKwPpjTyLMxFyOUey87cW+R1B6wJoYAaIpQhvM4VwMMowwBDIVyfby+pJ+NvUtxdkaoInhIRYCdURzzE1B/V7MLcdyh2gdYRATD7NpiChmgurxzrtLxUPU6ymq84AMZxcROiY8aWDigU1C+JBdPf0AqG+IOFQcZhlCHbNhUIdYE+w28MvARcw5jOl4+g/OBJEMc0LtylcKwPa5Lfbc8RES9GJBAwkmIWECoSJhCfUG8HQnuxb8cr1gHyQw8A1Cw/wcCXPUc0ho7Fr4BhLshxAkvh2NZkIwFw1mIMF52pO3sG9Z7V/jGIzvvobaLwAAAABJRU5ErkJggg==')
    baTIB = QByteArray.fromBase64(b'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')
    # pylint: enable=line-too-long
    self.wikipedia_pixmap = QPixmap() # https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Wikipedia_Logo_Mini.svg/240px-Wikipedia_Logo_Mini.svg.png
    self.wikipedia_pixmap.loadFromData(baWikipedia)
    self.wikidata_pixmap = QPixmap() #https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Wikidata-logo.png/234px-Wikidata-logo.png
    self.wikidata_pixmap.loadFromData(baWikidata)
    self.ols_pixmap = QPixmap() # https://www.ebi.ac.uk/ols/img/OLS_logo_2017.png
    self.ols_pixmap.loadFromData(baOLS)
    self.tib_pixmap = QPixmap() # https://service.tib.eu/ts4tib/img/TIB_Logo_en.png
    self.tib_pixmap.loadFromData(baTIB)


    #Widget setup
    self.mainL = QVBoxLayout()
    self.setLayout(self.mainL)
    self.setWindowTitle("Choose any definitions")
    self.setMinimumSize(QSize(1000,400))

    #ScrollArea
    self.scrollWidget = QWidget()
    self.scrollLayout = QVBoxLayout(self.scrollWidget)
    self.scrollWidget.setLayout(self.scrollLayout)
    self.scrollArea = QScrollArea()
    self.scrollArea.setWidgetResizable(True)
    self.scrollArea.setWidget(self.scrollWidget)
    self.mainL.addWidget(self.scrollArea)

    #Ok and Cancel Buttons
    btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
    self.buttonBox = QDialogButtonBox(btn)
    self.buttonBox.accepted.connect(self.finalize)
    self.buttonBox.rejected.connect(self.reject)
    self.mainL.addWidget(self.buttonBox)

    if self.search_term != "":
      self.wikipedia_search()
      self.wikidata_search()
      self.ols_search()
      self.tib_search()

    for widget in self.nested_widgets:
      self.scrollLayout.addWidget(widget)


  def finalize(self) -> None:
    """ what to do, when user clicks save """
    self.returnValues = [cb[1] for cb in self.listCB if cb[0].isChecked()]
    self.accept()
    return


  def wikipedia_search(self) -> None:
    """
    Search Wikipedia
    """
    number_of_results = 5
    base_url = "https://en.wikipedia.org/w/rest.php/v1/search/page"
    response = requests.get(base_url, params={'q': self.search_term, 'limit': number_of_results})  # type: ignore[arg-type]
    if response.status_code != 200:
      print(f"Wikidata: Request failed with status Code: {response.status_code}")
      return
    for page in json.loads(response.text)["pages"]:
      if page['description'] is not None and page['description'] != "Topics referred to by the same term":
        self.listCB.append((QCheckBox(page["title"]+": "+page["description"]),
                            "https://en.wikipedia.org/w/index.php?curid="+str(page["id"])))
        current = self.listCB[-1]
        self.nested_widgets.append(self.cb_and_image_widget(current[0], self.wikipedia_pixmap))
    return


  def wikidata_search(self) -> None:
    """
    Search Wikidata
    """
    base_url = "https://www.wikidata.org/w/api.php"
    response = requests.get(base_url, params={"search": self.search_term, \
                   "action":"wbsearchentities", "format":"json","language":"en","type":"item","continue":"0",})
    if response.status_code != 200:
      print(f"Wikidata: Request failed with status Code: {response.status_code}")
      return
    for result in json.loads(response.text)["search"]:
      a = result['display']
      if 'description' in a:
        label = a['label']
        description = a["description"]
        self.listCB.append((QCheckBox(label['value']+": "+description['value']), result["concepturi"]))
        current = self.listCB[-1]
        self.nested_widgets.append(self.cb_and_image_widget(current[0], self.wikidata_pixmap))
    return


  def ols_search(self) -> None:
    """
    Search Terminology server of OLS
    - some Ontologies do not provide a description in the json
    """
    base_url = "http://www.ebi.ac.uk/ols/api/search"
    response = requests.get(base_url, params= {"q": self.search_term})
    if response.status_code != 200:
      print(f"Ontology Lookup Service: Request failed with status Code: {response.status_code}")
      return
    for result in response.json()["response"]['docs']:
      if 'description' in result and result['description'] is not None:
        checkboxText = result["label"]+": "+"".join(result["description"])+" ("+result["ontology_name"]+")"
        self.listCB.append((QCheckBox(checkboxText), result["iri"]))
        current = self.listCB[-1]
        self.nested_widgets.append(self.cb_and_image_widget(current[0], self.ols_pixmap))
    return


  def tib_search(self) -> None:
    """
    Search Terminology server of TIB
    - some Ontologies do not provide a description in the json, this is handled by the devs of tib
    """
    base_url = "https://service.tib.eu/ts4tib/api/search"
    response = requests.get(base_url, params={"q": self.search_term})
    if response.status_code != 200: #useless for some errors because requests.get raises exceptions
      print(f"TIB Terminology Service: Request failed with status Code: {response.status_code}")
      return
    #ontologies that are both found in ols and tib:
    duplicate_ontos = ["afo", "bco", "bto", "chiro", "chmo", "duo", "edam", "efo", "fix", "hp", "iao", "mod", \
                       "mop", "ms", "nmrcv", "ncit", "obi", "om", "pato", "po", "proco", "prov", "rex", "ro", \
                       "rxno", "sbo", "sepio", "sio", "swo", "t4fs", "uo"]
    for result in response.json()["response"]['docs']:
      if 'description' in result and result['description'] is not None and \
        not result["ontology_name"] in duplicate_ontos:
        checkboxText = result["label"]+": "+"".join(result["description"])+" ("+result["ontology_name"]+")"
        self.listCB.append((QCheckBox(checkboxText), result["iri"]))
        current = self.listCB[-1]
        self.nested_widgets.append(self.cb_and_image_widget(current[0], self.tib_pixmap))
    return


  def pixmap_from_url(self, url:str) -> QPixmap:
    """ get pixmap from remote content

    Args:
      url (str): URL to download from

    Returns:
      QPixmap: image / logo
    """
    image = requests.get(url)
    pixmap = QPixmap()
    pixmap.loadFromData(image.content)
    pixmap = pixmap.scaled(40,40, Qt.KeepAspectRatio)
    return pixmap


  def cb_and_image_widget(self, checkbox:QCheckBox, pixmap:QPixmap) -> QWidget:
    """ add checkbod and logo into one widget and return it

    Args:
      checkbox (QCheckBox): checkbox to add
      pixmap   (QPixmap): pixmap to add

    Returns:
      QWidget: widget containing elements
    """
    nested_widget = QWidget()
    nested_widget.setStyleSheet("font-size: 17px")
    nested_layout = QHBoxLayout()
    nested_label = QLabel()
    nested_label.setPixmap(pixmap)
    nested_widget.setLayout(nested_layout)
    nested_layout.addWidget(checkbox)
    nested_layout.addWidget(nested_label)
    return nested_widget