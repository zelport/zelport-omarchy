import importlib.util
import json
import os
import pathlib
import tempfile
import sys
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / 'helper.py'
spec = importlib.util.spec_from_file_location('helper', PATH)
h = importlib.util.module_from_spec(spec) if PATH.exists() else None
if h: spec.loader.exec_module(h)


def state(port=8080):
    return dict(api_version=1, capabilities=['services', 'relay_status'], product='zelport', version='0.0.0', admin_url=f'http://localhost:{port}/', services=[dict(id='one', domain='demo.localhost', source_id='local', source_name='Local', state='configured', url=f'http://demo.localhost:{port}/')], connections=[])


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(h, 'bounded helper is implemented')

    def test_allowlist_and_urls(self):
        value = state(); value['token'] = 'SECRET'; value['services'][0]['upstream'] = 'SECRET'
        self.assertNotIn('SECRET', json.dumps(h.validate_state(value, 8080)))
        for url in ['https://demo.localhost:8080/', 'http://demo.localhost:8080/?x', 'http://demo.localhost:8080/#x', 'http://u@demo.localhost:8080/', 'http://evil.test:8080/', 'http://demo.localhost:8081/', 'http://demo.localhost:8080/evil', 'http://demo.localhost:8080/\\evil', 'http://demo.localhost:8080/?', 'http://demo.localhost:8080/#', 'http://demo.localhost:8080/\n']:
            with self.subTest(url=url), self.assertRaises(h.Failure): h.validate_url(url, 8080)
        self.assertEqual(h.validate_url('http://demo.localhost/', 80), 'http://demo.localhost/')
        self.assertEqual(h.validate_url('http://demo.localhost:8080',8080),'http://demo.localhost:8080')

    def test_optional_data_flow_is_display_only_and_validated(self):
        data = state()
        self.assertEqual(h.validate_state(data, 8080)['services'][0]['data_flow'], '')
        for flow in ['', 'Sandbox port 3000 → Aux port 5173', 'https://upstream.example/app']:
            data['services'][0]['data_flow'] = flow
            self.assertEqual(h.validate_state(data, 8080)['services'][0]['data_flow'], flow)
        for flow in [None, 42, 'x'*4097, 'bad\ntext']:
            data['services'][0]['data_flow'] = flow
            with self.subTest(flow=repr(flow)[:30]), self.assertRaises(h.Failure):
                h.validate_state(data, 8080)

    def test_absent_or_disconnected_relay_is_a_valid_integration_response(self):
        for connections in [[], [dict(id='ports_over_relay', label='Ports over Relay', state='disconnected')], [dict(id='relay', label='Built-in Relay', state='stopped')]]:
            data = state()
            data['connections'] = connections
            self.assertEqual(h.validate_state(data, 8080)['connections'], connections)

    def test_schema_identity_limits(self):
        for key, value in [('api_version', 2), ('product', 'other'), ('services', None), ('connections', {}), ('capabilities', []), ('services', state()['services'] * 4097)]:
            data = state(); data[key] = value
            with self.subTest(key=key), self.assertRaises(h.Failure): h.validate_state(data, 8080)
        data = state(); data['services'] *= 2
        with self.assertRaises(h.Failure): h.validate_state(data, 8080)



class TransportTests(unittest.TestCase):
    def test_isolated_http_and_sanitized_process(self):
        import http.server
        import subprocess
        import threading
        import time
        test = self
        class Handler(http.server.BaseHTTPRequestHandler):
            mode = 'ok'
            seen = []
            def log_message(self, *args): pass
            def do_GET(self):
                Handler.seen.append((self.path, self.headers.get('Host'), self.headers.get('Authorization')))
                if Handler.mode == 'timeout':
                    time.sleep(3)
                    return
                code = 302 if Handler.mode == 'redirect' else 401 if Handler.mode == 'unauthorized' else 200
                self.send_response(code)
                if code == 302: self.send_header('Location', '/secret')
                self.end_headers()
                value = state(self.server.server_port)
                value['token'] = 'SECRET'
                payload = b'x' * (1024*1024+1) if Handler.mode == 'large' else b'{' if Handler.mode == 'malformed' else json.dumps(value).encode()
                try: self.wfile.write(payload)
                except (BrokenPipeError, ConnectionResetError): pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1',0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            with tempfile.TemporaryDirectory() as directory:
                directory = os.path.realpath(directory)
                root = pathlib.Path(directory); target = root/'zelport'; target.mkdir()
                (target/'endpoint.json').write_text(json.dumps({'port':server.server_port}))
                for mode, expected in [('ok',None), ('redirect','unavailable'), ('unauthorized','unauthorized'), ('large','limit'), ('malformed','invalid'), ('timeout','timeout')]:
                    Handler.mode = mode; before = len(Handler.seen)
                    started = time.monotonic()
                    if expected:
                        with self.assertRaises(h.Failure) as caught:
                            h.probe(server.server_port)
                        self.assertEqual(str(caught.exception),expected)
                    else:
                        result = h.probe(server.server_port)
                        self.assertNotIn('SECRET',json.dumps(result))
                    self.assertLess(time.monotonic()-started,1.5)
                    self.assertEqual(len(Handler.seen)-before,1)
                    self.assertEqual(Handler.seen[-1],('/api/integration/v1/state',f'localhost:{server.server_port}',None))

        finally: server.shutdown(); server.server_close()

if __name__ == '__main__': unittest.main()
