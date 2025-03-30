import unittest

from spectator import MonotonicCounter, MemoryWriter, MeterId


class MonotonicCounterTest(unittest.TestCase):
    tid = MeterId("monotonic_counter")

    def test_set(self):
        c = MonotonicCounter(self.tid, writer=MemoryWriter())
        self.assertTrue(c.writer().is_empty())

        c.set(1)
        self.assertEqual("C:monotonic_counter:1", c.writer().last_line())

    def test_set_negative(self):
        c = MonotonicCounter(self.tid, writer=MemoryWriter())
        self.assertTrue(c.writer().is_empty())

        c.set(-1)
        self.assertEqual("C:monotonic_counter:-1", c.writer().last_line())
