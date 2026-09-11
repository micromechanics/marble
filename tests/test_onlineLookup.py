"""Tests for the current online lookup request and response contract."""
import io
from types import SimpleNamespace

from pymarble.onlineLookup import _responseText, buildLookupPayload, lookup
from pymarble.section import Section


def test_buildLookupPayload_collects_available_format_clues() -> None:
  binaryFile = SimpleNamespace(fileName='/data/person.dat', fileLength=32, file=io.BytesIO(bytes(range(32))),
    meta={'vendor':'vendor', 'label':'label', 'software':'software', 'endian':'small'},
    content={0:Section(length=4, dType='i', key='record count'),
             16:Section(length=4, dType='f', key='signal')})

  payload = buildLookupPayload(binaryFile)

  assert payload['extension'] == '.dat'
  assert payload['base_name'] == 'person.dat'
  assert payload['size_bytes'] == 32
  assert payload['first_64_bytes_hex'] == bytes(range(32)).hex()
  assert payload['automatic_identification_findings'] == ['record count', 'signal', 'vendor: vendor', 'label: label', 'software: software']


def test_lookup_uses_responses_api_and_includes_returned_sources(monkeypatch) -> None:
  binaryFile = SimpleNamespace(fileName='/data/sample.dat', fileLength=4, file=io.BytesIO(b'ABCD'),
    meta={'vendor':'', 'label':'', 'software':'', 'endian':'small'}, content={})
  captured = {}

  def fakePost(url, key, body):
    captured.update(url=url, key=key, body=body)
    return {'output_text':'Likely a data format.', 'url':'https://example.com/format'}
  monkeypatch.setattr('pymarble.onlineLookup._post', fakePost)

  report = lookup(binaryFile, {'llm':{'type':'openAI', 'server':'https://example.invalid/v1', 'model':'model',
                                      'keyStorage':'plaintext', 'apiKey':'key'}})

  assert captured['url'] == 'https://example.invalid/v1/responses'
  assert captured['key'] == 'key'
  assert captured['body']['tools'] == [{'type':'web_search_preview'}]
  assert report == 'WEB-ASSISTED LOOKUP\n\nLikely a data format.\n\nSources reported by the server:\nhttps://example.com/format'


def test_responseText_reads_nested_responses_content() -> None:
  response = {'output':[{'content':[{'type':'output_text', 'text':'first'}, {'type':'text', 'text':'second'}]}]}

  assert _responseText(response) == 'first\nsecond'
