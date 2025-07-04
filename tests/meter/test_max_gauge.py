import unittest

from spectator import MaxGauge, MemoryWriter, MeterId, NoopWriter


class MaxGaugeTest(unittest.TestCase):
    tid = MeterId("max_gauge")

    def test_noop_writer(self):
        g = MaxGauge(self.tid)
        self.assertTrue(isinstance(g.writer(), NoopWriter))

    def test_set(self):
        g = MaxGauge(self.tid, MemoryWriter())
        self.assertTrue(g.writer().is_empty())

        g.set(0)
        self.assertEqual("m:max_gauge:0", g.writer().last_line())
