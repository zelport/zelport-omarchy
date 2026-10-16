#!/usr/bin/env python3
"""Read one local endpoint hint and poll the loopback integration API."""
import http.client
import json
import os
import re
import signal
import stat
import time

LIMIT = 1024 * 1024


class Failure(Exception):
    pass


class Deadline(BaseException):
    pass


def validate_config(data):
    defaults = {'version': 1,
                'services': {'source_types': [], 'sort_by': 'domain'},
                'panel': {'remember_selection': True, 'clear_search_on_open': True}}
    # Ignore the retired gateway selector in existing plugin configuration.
    if isinstance(data, dict): data = {k: v for k, v in data.items() if k != 'gateway'}
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1 or set(data) - set(defaults):
        raise Failure('invalid_config')
    for section in ('services', 'panel'):
        value = data.get(section, {})
        if not isinstance(value, dict) or set(value) - set(defaults[section]): raise Failure('invalid_config')
        defaults[section].update(value)
    sources = defaults['services']['source_types']
    if not isinstance(sources, list) or len(sources) > 64 or not all(isinstance(x, str) and re.fullmatch(r'[a-z][a-z0-9_]{0,63}', x) for x in sources): raise Failure('invalid_config')
    if defaults['services']['sort_by'] not in ('domain', 'source_type', 'state'): raise Failure('invalid_config')
    if any(type(v) is not bool for v in defaults['panel'].values()): raise Failure('invalid_config')
    return defaults


def load_config():
    base = os.environ.get('XDG_CONFIG_HOME', '')
    if not os.path.isabs(base): base = os.path.expanduser('~/.config')
    path = os.path.join(base, 'zelport', 'omarchy.json')
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    except FileNotFoundError:
        return validate_config({'version': 1})
    except OSError:
        raise Failure('invalid_config') from None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode): raise Failure('invalid_config')
        raw = os.read(fd, 16385)
        if len(raw) > 16384: raise Failure('invalid_config')
        return validate_config(json.loads(raw))
    except (ValueError, OSError):
        raise Failure('invalid_config') from None
    finally:
        os.close(fd)


def text(value, limit=512):
    if not isinstance(value, str) or not value or len(value) > limit or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise Failure('invalid')
    return value


def validate_url(value, port, admin=False):
    text(value, 512)
    host = r'localhost' if admin else r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+localhost'
    suffix = '' if port == 80 else ':' + str(port)
    if not re.fullmatch(r'http://' + host + re.escape(suffix) + r'/?', value):
        raise Failure('invalid')
    return value


def validate_state(data, port):
    if not isinstance(data, dict): raise Failure('invalid')
    if type(data.get('api_version')) is not int or data['api_version'] != 1: raise Failure('incompatible')
    if data.get('product') != 'zelport': raise Failure('incompatible')
    caps = data.get('capabilities')
    if not isinstance(caps, list) or len(caps) > 32 or not all(isinstance(x, str) for x in caps) or 'services' not in caps or 'relay_status' not in caps: raise Failure('incompatible')
    services, connections = data.get('services'), data.get('connections')
    if not isinstance(services, list) or not isinstance(connections, list): raise Failure('invalid')
    if len(services) > 4096 or len(connections) > 64: raise Failure('limit')
    clean = dict(api_version=1, version=text(data.get('version')), admin_url=validate_url(data.get('admin_url'), port, True), services=[], connections=[])
    for source, dest, fields in [(services, clean['services'], ['id','domain','source_id','source_name','state','url']), (connections, clean['connections'], ['id','label','state'])]:
        seen = set()
        for row in source:
            if not isinstance(row, dict): raise Failure('invalid')
            item = {key: text(row.get(key)) for key in fields}
            if item['id'] in seen: raise Failure('invalid')
            seen.add(item['id'])
            if 'url' in item:
                validate_url(item['url'], port)
                flow = row.get('data_flow', '')
                item['data_flow'] = '' if flow == '' else text(flow, 4096)
            dest.append(item)
    return clean


def endpoint_port():
    base = os.environ.get('XDG_STATE_HOME', '')
    if not os.path.isabs(base): base = os.path.expanduser('~/.local/state')
    path = os.path.join(base, 'zelport', 'endpoint.json')
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode): return 8080
            raw = os.read(fd, 4097)
            if len(raw) > 4096: return 8080
            data = json.loads(raw)
        finally:
            os.close(fd)
        port = data.get('port') if isinstance(data, dict) else None
        if type(port) is int and 1 <= port <= 65535: return port
    except (OSError, ValueError):
        pass
    return 8080


def request(port):
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=0.8)
    try:
        authority = 'localhost' if port == 80 else 'localhost:' + str(port)
        connection.request('GET', '/api/integration/v1/state', headers={'Host': authority, 'Accept': 'application/json'})
        response = connection.getresponse()
        if response.status == 401: raise Failure('unauthorized')
        if response.status != 200: raise Failure('unavailable')
        if response.getheader('Content-Encoding', 'identity') != 'identity': raise Failure('invalid')
        raw = response.read(LIMIT + 1)
        if len(raw) > LIMIT: raise Failure('limit')
        try: data = json.loads(raw)
        except ValueError: raise Failure('invalid') from None
        return validate_state(data, port)
    finally:
        connection.close()


def probe(port, budget=0.9):
    # Bound the entire response, including slow streaming bodies.
    remaining, interval = signal.getitimer(signal.ITIMER_REAL)
    previous = signal.signal(signal.SIGALRM, deadline)
    started = time.monotonic()
    signal.setitimer(signal.ITIMER_REAL, min(budget, remaining) if remaining else budget)
    try:
        return request(port)
    except (Deadline, TimeoutError):
        raise Failure('timeout') from None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        if remaining:
            left = remaining - (time.monotonic() - started)
            if left <= 0: raise Deadline()
            signal.setitimer(signal.ITIMER_REAL, left, interval)


def poll():
    port = endpoint_port()
    ports = [port] if port == 8080 else [port, 8080]
    error = 'unavailable'
    for candidate in ports:
        try: return {'ok': True, 'state': probe(candidate)}
        except Failure as failure: error = str(failure)
        except TimeoutError: error = 'timeout'
        except (OSError, ValueError, http.client.HTTPException): error = 'unavailable'
    return {'ok': False, 'error': error}


def deadline(signum, frame):
    raise Deadline()


def main():
    result = {'ok': False, 'error': 'unavailable'}
    try:
        signal.signal(signal.SIGALRM, deadline)
        signal.setitimer(signal.ITIMER_REAL, 2)
        config = load_config()
        result['config'] = config
        result.update(poll())
        if result['ok']: result.pop('error', None)
    except Deadline:
        result['error'] = 'timeout'
    except Failure as failure:
        result['error'] = str(failure)
    except Exception:
        pass
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps(result, separators=(',', ':')))


if __name__ == '__main__': main()
