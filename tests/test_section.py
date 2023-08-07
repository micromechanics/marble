from pymarble.section import Section

def testSection():
  s0 = Section()
  assert len(s0.__repr__())>20, '__repr__ string not long enough'  #test representation=print exists
  assert len(s0.toCSV())>11,    'CSV output not long enough'
  assert s0.byteSize()==-1,     'length of void Section should be -1'
  assert s0.size()=='0',        'size of void Section should be 0'
  assert len(s0.pythonHeader())>2000, 'header should be long'

  s1 = Section(length=3, dType='i', key='test key', unit='-', value='3 ints', link='www.google.com', dClass='metadata')
  assert len(s1.__repr__())>60, '__repr__ string not long enough'  #test representation=print exists
  assert len(s1.toCSV())>11,    'CSV output not long enough'
  assert s1.byteSize()==12,     'length of void Section should be -1'
  assert s1.size()=='3i',       'size of void Section should be 0'
  assert len(s1.pythonHeader())>2000, 'header should be long'

  s2 = Section()
  s2.setData('3|i|test key|-|www.google.com|metadata||3|0|1.0|False|3 ints')
  assert len(s2.__repr__())>60, '__repr__ string not long enough'  #test representation=print exists
  assert len(s2.toCSV())>11,    'CSV output not long enough'
  assert s2.byteSize()==12,     'length of void Section should be -1'
  assert s2.size()=='3i',       'size of void Section should be 0'
  assert len(s2.pythonHeader())>2000, 'header should be long'

  s3 = Section(data='3|i|test key|-|www.google.com|metadata||3|0|1.0|False|3 ints')
  assert len(s3.__repr__())>60, '__repr__ string not long enough'  #test representation=print exists
  assert len(s3.toCSV())>11,    'CSV output not long enough'
  assert s3.byteSize()==12,     'length of void Section should be -1'
  assert s3.size()=='3i',       'size of void Section should be 0'
  assert len(s3.pythonHeader())>2000, 'header should be long'

  # every function is tested except of toPY
