import unittest

from spectator import MeterId


class MeterIdTest(unittest.TestCase):

    def test_different_types_not_equal(self):
        id1 = MeterId("foo", {"a": "1"})
        self.assertTrue(id1 != 1)

    def test_equals_same_name(self):
        id1 = MeterId("foo")
        id2 = MeterId("foo")
        self.assertEqual(id1, id2)

    def test_equals_same_tags(self):
        id1 = MeterId("foo", {"a": "1", "b": "2", "c": "3"})
        id2 = MeterId("foo", {"c": "3", "b": "2", "a": "1"})
        self.assertEqual(id1, id2)

    def test_hash_same_tags(self):
        id1 = MeterId("foo", {"a": "1", "b": "2", "c": "3"})
        id2 = MeterId("foo", {"c": "3", "b": "2", "a": "1"})
        self.assertEqual(hash(id1), hash(id2))

    def test_illegal_chars_are_replaced(self):
        id = MeterId("test`!@#$%^&*()-=~_+[]{}\\|;:'\",<.>/?foo")
        self.assertEqual("test______^____-_~______________.___foo", id.spectatord_id)

    def test_invalid_tags(self):
        expected_messages = [
            "WARNING:spectator.meter.meter_id:MeterId(name=foo, tags={'k': ''}) is invalid due to tag keys or values which are not strings or are zero-length strings; proceeding with truncated tags MeterId(name=foo, tags={})",
            "WARNING:spectator.meter.meter_id:MeterId(name=bar, tags={'k': 1}) is invalid due to tag keys or values which are not strings or are zero-length strings; proceeding with truncated tags MeterId(name=bar, tags={})",
            "WARNING:spectator.meter.meter_id:MeterId(name=baz, tags={1: 'v'}) is invalid due to tag keys or values which are not strings or are zero-length strings; proceeding with truncated tags MeterId(name=baz, tags={})",
            "WARNING:spectator.meter.meter_id:MeterId(name=quux, tags={'k': 'v', 1: 'v'}) is invalid due to tag keys or values which are not strings or are zero-length strings; proceeding with truncated tags MeterId(name=quux, tags={'k': 'v'})",
        ]

        with self.assertLogs("spectator.meter.meter_id", level='INFO') as logs:
            id1 = MeterId("foo", {"k": ""})
            self.assertEqual("MeterId(name=foo, tags={})", str(id1))
            id2 = MeterId("bar", {"k": 1})
            self.assertEqual("MeterId(name=bar, tags={})", str(id2))
            id3 = MeterId("baz", {1: "v"})
            self.assertEqual("MeterId(name=baz, tags={})", str(id3))
            id4 = MeterId("quux", {"k": "v", 1: "v"})
            self.assertEqual("MeterId(name=quux, tags={'k': 'v'})", str(id4))

        self.assertEqual(expected_messages, logs.output)

    def test_lookup_tags(self):
        id1 = MeterId("foo", {"a": "1", "b": "2", "c": "3"})
        id2 = MeterId("foo", {"c": "3", "b": "2", "a": "1"})
        d = {id1: "test"}
        self.assertEqual("test", d[id2])

    def test_name(self):
        id1 = MeterId("foo", {"a": "1"})
        self.assertEqual("foo", id1.name())

    def test_spectatord_id(self):
        id1 = MeterId("foo")
        self.assertEqual("foo", id1.spectatord_id)

        id2 = MeterId("bar", {"a": "1"})
        self.assertEqual("bar,a=1", id2.spectatord_id)

        id3 = MeterId("baz", {"a": "1", "b": "2"})
        self.assertEqual("baz,a=1,b=2", id3.spectatord_id)

    def test_str(self):
        id1 = MeterId("foo")
        self.assertEqual("MeterId(name=foo, tags={})", str(id1))

        id2 = MeterId("bar", {"a": "1"})
        self.assertEqual("MeterId(name=bar, tags={'a': '1'})", str(id2))

        id3 = MeterId("baz", {"a": "1", "b": "2", "c": "3"})
        self.assertEqual("MeterId(name=baz, tags={'a': '1', 'b': '2', 'c': '3'})", str(id3))

    def test_tags(self):
        id1 = MeterId("foo", {"a": "1"})
        self.assertEqual({"a": "1"}, id1.tags())

    def test_tags_defensive_copy(self):
        id1 = MeterId("foo", {"a": "1"})
        tags = id1.tags()
        tags["b"] = "2"
        self.assertEqual({"a": "1", "b": "2"}, tags)
        self.assertEqual({"a": "1"}, id1.tags())

    def test_with_tag_returns_new_object(self):
        id1 = MeterId("foo")
        id2 = id1.with_tag("a", "1")
        self.assertNotEqual(id1, id2)
        self.assertEqual({}, id1.tags())
        self.assertEqual({"a": "1"}, id2.tags())

    def test_with_tags_returns_new_object(self):
        id1 = MeterId("foo")
        id2 = id1.with_tags({"a": "1", "b": "2"})
        self.assertNotEqual(id1, id2)
        self.assertEqual({}, id1.tags())
        self.assertEqual({"a": "1", "b": "2"}, id2.tags())

    def test_empty_with_tags_returns_same_object(self):
        id1 = MeterId("foo")
        id2 = id1.with_tags({})
        self.assertEqual(id1, id2)
