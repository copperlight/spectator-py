import unittest

from spectator import MemoryWriter, MeterId, NoopWriter, PercentileDistributionSummary


class PercentileDistributionSummaryTest(unittest.TestCase):
    tid = MeterId("percentile_dist_summary")

    def test_noop_writer(self):
        d = PercentileDistributionSummary(self.tid)
        self.assertTrue(isinstance(d.writer(), NoopWriter))

    def test_record(self):
        d = PercentileDistributionSummary(self.tid, writer=MemoryWriter())
        self.assertTrue(d.writer().is_empty())

        d.record(42)
        self.assertEqual("D:percentile_dist_summary:42", d.writer().last_line())

    def test_record_negative(self):
        d = PercentileDistributionSummary(self.tid, writer=MemoryWriter())
        d.record(-42)
        self.assertTrue(d.writer().is_empty())

    def test_record_zero(self):
        d = PercentileDistributionSummary(self.tid, writer=MemoryWriter())
        d.record(0)
        self.assertEqual("D:percentile_dist_summary:0", d.writer().last_line())
