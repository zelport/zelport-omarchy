import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_helper import h

class ConfigTests(unittest.TestCase):
    def test_defaults_precedence_and_live_reload(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'XDG_CONFIG_HOME':d,'ZELPORT_INTEGRATION_PORT':'8070'}, clear=True):
            self.assertNotIn('gateway',h.load_config())
            p=Path(d)/'zelport/omarchy.json';p.parent.mkdir();p.write_text('{"version":1}')
            self.assertNotIn('gateway',h.load_config())
            p.write_text('{"version":1,"gateway":{"port":9090}}')
            self.assertNotIn('gateway',h.load_config())
            p.write_text('{')
            with self.assertRaisesRegex(h.Failure,'invalid_config'):h.load_config()
    def test_strict_config(self):
        for data in [[],{'version':2},{'version':True},{'version':1,'gatway':{}},{'version':1,'panel':{'remember_selection':'yes'}},{'version':1,'services':{'sort_by':'whatever'}},{'version':1,'services':{'source_types':['bad type']}}]:
            with self.subTest(data=data),self.assertRaisesRegex(h.Failure,'invalid_config'):h.validate_config(data)
        c=h.validate_config({'version':1,'services':{'source_types':['remote_http'],'sort_by':'state'},'panel':{'clear_search_on_open':False}})
        self.assertFalse(c['panel']['clear_search_on_open'])
        self.assertTrue(c['panel']['remember_selection'])
