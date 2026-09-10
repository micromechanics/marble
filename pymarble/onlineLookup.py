"""Privacy-conserving online file-format lookup"""
import json, os, string
from typing import Any
from urllib import error, request


class LookupRequestError(RuntimeError):
  """A request failure and whether a text-only fallback is appropriate"""
  def __init__(self, message:str, allowFallback:bool=False):
    super().__init__(message)
    self.allowFallback = allowFallback


def buildLookupPayload(binaryFile:Any) -> dict[str, Any]:
  """Build the deliberately small set of local clues allowed for lookup"""
  binaryFile.file.seek(0)
  firstBytes = binaryFile.file.read(64)
  binaryFile.file.seek(0)
  printable = ''.join(chr(byte) if chr(byte) in string.printable and byte not in (11, 12) else '.' for byte in firstBytes)
  findings = []
  for section in binaryFile.content.values():
    if key:= str(getattr(section, 'key', '')).strip():
      findings.append(key)
  for key in ('vendor', 'label', 'software'):
    if binaryFile.meta.get(key):
      findings.append(f'{key}: {binaryFile.meta[key]}')
  return {'extension':os.path.splitext(binaryFile.fileName)[1], 'base_name':os.path.basename(binaryFile.fileName),
          'size_bytes':binaryFile.fileLength, 'first_64_bytes_hex':firstBytes.hex(),
          'first_64_bytes_printable':printable, 'automatic_identification_findings':findings[:12]}


def getApiKey(configuration:dict[str, Any]) -> str:
  """Read a key from the configured keyring, or an explicitly accepted fallback"""
  llm = configuration.get('llm', {})
  if llm.get('keyStorage', 'keyring') == 'plaintext':
    return str(llm.get('apiKey', ''))
  try:
    import keyring
    return keyring.get_password('pymarble', str(llm.get('keyringId', ''))) or ''
  except Exception:  # a missing or unusable backend means no usable configuration
    return ''


def _post(url:str, key:str, body:dict[str, Any]) -> dict[str, Any]:
  data = json.dumps(body).encode('utf-8')
  headers = {'Content-Type':'application/json', 'Authorization':f'Bearer {key}'}
  try:
    with request.urlopen(request.Request(url, data=data, headers=headers, method='POST'), timeout=45) as response:
      return json.loads(response.read().decode('utf-8'))
  except error.HTTPError as exc:
    raise LookupRequestError(f'server returned HTTP {exc.code}', exc.code in (400, 404, 405, 422)) from exc
  except error.URLError as exc:
    raise LookupRequestError('could not reach the configured server') from exc
  except TimeoutError as exc:
    raise LookupRequestError('the configured server did not respond in time') from exc


def _responseText(response:dict[str, Any]) -> str:
  if isinstance(response.get('output_text'), str):
    return response['output_text']
  texts = []
  for output in response.get('output', []):
    for content in output.get('content', []):
      if content.get('type') in ('output_text', 'text') and isinstance(content.get('text'), str):
        texts.append(content['text'])
  return '\n'.join(texts)


def _urls(value:Any) -> list[str]:
  if isinstance(value, dict):
    found = [item for key, item in value.items() if key == 'url' and isinstance(item, str)]
    for item in value.values():
      found.extend(_urls(item))
    return found
  if isinstance(value, list):
    return [url for item in value for url in _urls(item)]
  return []


def lookup(binaryFile:Any, configuration:dict[str, Any]) -> str:
  """Perform a lookup without changing ``binaryFile`` or logging credentials/clues"""
  llm = {'type':'openAI', 'server':'https://api.openai.com/v1', 'model':'',
         'keyringId':'pymarble-openai-default', 'comment':'', 'keyStorage':'keyring'} | configuration.get('llm', {})
  if llm.get('type') != 'openAI' or not llm.get('server') or not llm.get('model'):
    return 'Online lookup unavailable: configure an OpenAI-compatible server and model first'
  key = getApiKey(configuration)
  if not key:
    return 'Online lookup unavailable: configure an API key first'
  baseUrl = str(llm['server']).rstrip('/')
  clues = buildLookupPayload(binaryFile)
  promptBase = ('You help a scientist inspect an unknown binary file. Use only the local clues below; '
                'never ask for or infer a file upload. Return concise practical plain text. ')
  webInstruction = ('Clearly separate web-derived evidence (with direct source URLs and what each establishes) '
                    'from interpretation based only on the local clues.')
  guidance = (" State uncertainty plainly. Identify a probable format, vendor, or instrument family only when "
              "supported. If a maintained public parser/library is appropriate, prominently say exactly: "
              "'Use that parser rather than MARBLE for decoding this format.' Otherwise suggest useful MARBLE "
              'next steps such as header offsets, record sizes, numeric types, byte order, or terminology. '
              'Do not present guesses as facts.\n\nLocal clues:\n')
  prompt = promptBase + webInstruction + guidance + json.dumps(clues, ensure_ascii=False)
  try:
    response = _post(f'{baseUrl}/responses', key, {'model':llm['model'], 'input':prompt,
                     'tools':[{'type':'web_search_preview'}]})
    report = _responseText(response).strip()
    if not report:
      raise LookupRequestError('server returned no report', True)
    urls = list(dict.fromkeys(_urls(response)))
    if urls and not any(url in report for url in urls):
      report += '\n\nSources reported by the server:\n' + '\n'.join(urls)
    return 'WEB-ASSISTED LOOKUP\n\n' + report
  except LookupRequestError as webError:
    if not webError.allowFallback:
      return f'Online lookup unavailable: {webError}'
    try:
      fallbackInstruction = ('Web searching is unavailable. Do not claim web research, citations, or source URLs; '
                             'provide only an interpretation of the local clues.')
      fallbackPrompt = promptBase + fallbackInstruction + guidance + json.dumps(clues, ensure_ascii=False)
      response = _post(f'{baseUrl}/chat/completions', key, {'model':llm['model'],
                       'messages':[{'role':'user', 'content':fallbackPrompt}], 'temperature':0.2})
      choices = response.get('choices', [])
      report = choices[0].get('message', {}).get('content', '').strip() if choices else ''
      if not report:
        raise LookupRequestError('server returned no report') from webError
      return 'LLM-ONLY INTERPRETATION (no web evidence)\n\n' + report
    except LookupRequestError:
      return f'Online lookup unavailable: {webError}'
