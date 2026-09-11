"""Tests for sanitized evidence and bounded local inspections."""
import io, struct
from types import SimpleNamespace

from pymarble.onlineLookup import buildLookupPayload, inspectionError, requestAnalysis, runInspection
from pymarble.section import Section


def test_buildLookupPayload_excludes_text_and_raw_bytes() -> None:
  binaryFile = SimpleNamespace(fileName='/private/person.dat', fileLength=32, file=io.BytesIO(bytes(range(32))),
    meta={'vendor':'private vendor', 'label':'private label', 'software':'private software', 'endian':'small'},
    periodicity={'count':4}, rowFormatMeta=[{'key':'private', 'unit':'private'}], rowFormatSegments={16},
    content={0:Section(length=4, dType='i', key='private count', value='private text', dClass='count', prob=100),
             16:Section(length=4, dType='f', key='private signal', unit='private', shape=[4], dClass='primary', prob=75)})
  binaryFile.file.seek(7)

  payload = buildLookupPayload(binaryFile)
  serialized = str(payload)

  assert binaryFile.file.tell() == 7
  assert 'private vendor' not in serialized
  assert 'private label' not in serialized
  assert 'private text' not in serialized
  assert 'private signal' not in serialized
  assert 'hex' not in serialized
  assert payload['sections'][0]['numeric_summary'] == {'count':4, 'finite_count':4, 'non_finite_count':0,
                                                       'minimum':50462976, 'maximum':252579084}
  assert payload['string_regions']['character_data_sent'] is False


def test_runInspection_is_bounded_and_text_free() -> None:
  binaryFile = SimpleNamespace(fileLength=32, file=io.BytesIO(bytes(range(32))), meta={'endian':'small'},
    content={0:Section(length=32, dType='b')})

  assert inspectionError({'name':'byte_profile', 'arguments':{'offset':0, 'size':256}}, 32) == ''
  assert inspectionError({'name':'unknown', 'arguments':{}}, 32) == 'unknown inspection'
  assert inspectionError({'name':'byte_profile', 'arguments':{'offset':0, 'size':4097}}, 32)
  result = runInspection(binaryFile, {'name':'byte_profile', 'arguments':{'offset':0, 'size':32}})
  assert result['profile']['length'] == 32
  assert 'values' not in result


def test_requestAnalysis_final_payload_excludes_private_text(monkeypatch) -> None:
  binaryFile = SimpleNamespace(fileName='/private/person.dat', fileLength=16, file=io.BytesIO(b'private contents!'),
    meta={'vendor':'private vendor', 'label':'private label', 'software':'private software', 'endian':'small'},
    periodicity={}, rowFormatMeta=[], rowFormatSegments=set(), content={0:Section(length=16, dType='c', value='private')})
  captured = {}

  def fakePost(url, key, body):
    captured['body'] = body
    return {'output_text':'{"report":"safe","actions":[]}'}
  monkeypatch.setattr('pymarble.onlineLookup._post', fakePost)

  result = requestAnalysis(binaryFile, {'llm':{'type':'openAI', 'server':'https://example.invalid', 'model':'model',
                                                'keyStorage':'plaintext', 'apiKey':'key'}})

  serialized = str(captured['body'])
  assert result['report'] == 'safe'
  assert 'person.dat' not in serialized
  assert 'private contents' not in serialized
  assert 'private vendor' not in serialized


def test_export_summary_preserves_columns_and_comparison(tmp_path) -> None:
  export = tmp_path/'export.txt'
  export.write_text('private 1.0 2.0\nprivate 3.0 4.0\n', encoding='utf-8')
  binaryFile = SimpleNamespace(fileLength=8, file=io.BytesIO(struct.pack('<2f', 1.0, 3.0)), meta={'endian':'small'}, content={})

  summary = runInspection(binaryFile, {'name':'export_numeric_summary', 'arguments':{'artifact_index':0}}, [str(export)])
  comparison = runInspection(binaryFile, {'name':'export_numeric_comparison',
    'arguments':{'artifact_index':0, 'column':1, 'offset':0, 'size':8, 'dtype':'f', 'byte_order':'little'}}, [str(export)])

  assert summary['artifact']['columns'][0]['numeric_count'] == 0
  assert summary['artifact']['columns'][1]['numeric_count'] == 2
  assert comparison['maximum_absolute_difference'] == 0


def test_entropy_and_repetition_are_distinct_inspections() -> None:
  binaryFile = SimpleNamespace(fileLength=16, file=io.BytesIO(b'abcdabcdabcdabcd'), meta={'endian':'small'}, content={})

  entropy = runInspection(binaryFile, {'name':'entropy', 'arguments':{'offset':0, 'size':16}})
  repetition = runInspection(binaryFile, {'name':'repeated_records', 'arguments':{'offset':0, 'size':16, 'record_size':4}})

  assert 'windows' in entropy
  assert repetition['adjacent_equal_records'] == 3
  assert repetition['constant_byte_positions'] == 4
