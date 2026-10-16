"""Narrow source contract guard, not a QML parser or native load test."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HostInjectionTests(unittest.TestCase):
    def test_panel_host_injected_properties_are_writable(self):
        # v4.0.4 shell.qml panelLoader.onLoaded assigns these when declared.
        assigned = {'omarchyPath', 'shell', 'manifest', 'barWidgetRegistry', 'pluginRegistry', 'service'}
        declarations = re.findall(r'^    (readonly )?property \w+ (\w+)\s*:', (ROOT/'Panel.qml').read_text(), re.M)
        for readonly, name in declarations:
            if name in assigned:
                self.assertFalse(readonly, name + ' must accept the host assignment before panel registration')
