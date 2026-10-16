import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_helper import h, state

class EndpointTests(unittest.TestCase):
    def test_paths_missing_invalid_and_reload(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'HOME':d, 'XDG_STATE_HOME':'relative'}, clear=True):
            p=Path(d)/'.local/state/zelport/endpoint.json'
            self.assertEqual(h.endpoint_port(),8080)
            p.parent.mkdir(parents=True)
            for value in ['{', '[]', '{"port":true}', '{"port":0}', '{"port":65536}', 'x'*4097]:
                p.write_text(value);self.assertEqual(h.endpoint_port(),8080)
            p.write_text('{"port":8081}')
            self.assertEqual(h.endpoint_port(),8081)
            p.write_text('{"port":8082}')
            self.assertEqual(h.endpoint_port(),8082)
            with patch.dict(os.environ, {'XDG_STATE_HOME':d}): self.assertEqual(h.endpoint_port(),8080)
            p.unlink();os.mkfifo(p)
            self.assertEqual(h.endpoint_port(),8080)

    def test_default_fallback_order_and_no_scan(self):
        with patch.object(h,'endpoint_port',return_value=8081), patch.object(h,'probe',side_effect=[h.Failure('unavailable'),state()]) as probe:
            self.assertTrue(h.poll()['ok'])
            self.assertEqual([c.args[0] for c in probe.call_args_list],[8081,8080])
        with patch.object(h,'endpoint_port',return_value=8080), patch.object(h,'probe',side_effect=h.Failure('incompatible')) as probe:
            self.assertEqual(h.poll()['error'],'incompatible')
            probe.assert_called_once_with(8080)
        with patch.object(h,'endpoint_port',return_value=8081), patch.object(h,'probe',return_value=state(8081)) as probe:
            self.assertTrue(h.poll()['ok'])
            probe.assert_called_once_with(8081)

    def test_process_reads_hint_without_runtime_directory_and_reloads(self):
        import http.server
        import subprocess
        import sys
        import threading
        from test_helper import PATH
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                self.send_response(200);self.end_headers()
                self.wfile.write(json.dumps(state(self.server.server_port)).encode())
        servers=[]
        try:
            for _ in range(2):
                server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
                threading.Thread(target=server.serve_forever,daemon=True).start();servers.append(server)
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'zelport/endpoint.json';p.parent.mkdir()
                env={**os.environ,'XDG_STATE_HOME':d,'XDG_CONFIG_HOME':d,'XDG_RUNTIME_DIR':'','http_proxy':'http://127.0.0.1:1'}
                for server in servers:
                    p.write_text(json.dumps({'port':server.server_port}))
                    result=subprocess.run([sys.executable,str(PATH)],env=env,capture_output=True,text=True,timeout=3)
                    self.assertEqual(result.stderr,'')
                    data=json.loads(result.stdout)
                    self.assertTrue(data['ok'],data)
                    self.assertEqual(data['state']['admin_url'],f'http://localhost:{server.server_port}/')
        finally:
            for server in servers:server.shutdown();server.server_close()
