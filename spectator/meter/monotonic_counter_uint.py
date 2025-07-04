from ctypes import c_uint64
from typing import Optional

from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import WriterUnion
from spectator.writer.noop_writer import NoopWriter


class MonotonicCounterUint(Meter):
    """The value is a monotonically increasing number of an uint64 data type. These kinds of
    values are commonly seen in networking metrics, such as bytes-per-second. A minimum of two
    samples must be received in order for SpectatorD to calculate a delta value and report it to
    the backend."""

    def __init__(self, meter_id: MeterId, writer: Optional[WriterUnion] = None) -> None:
        if writer is None:
            writer = NoopWriter()

        super().__init__(meter_id, writer, "U")

    def set(self, amount: c_uint64) -> None:
        line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{amount.value}"
        self._writer.write(line)
