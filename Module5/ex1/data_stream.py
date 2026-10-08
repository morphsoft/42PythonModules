import typing
from abc import ABC, abstractmethod


class DataProcessor(ABC):
    """Common interface shared by every data processor."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._storage: list[str] = []
        self._next_rank = 0

    @property
    def name(self) -> str:
        """Human readable name of the processor."""
        return self._name

    @property
    def total(self) -> int:
        """Number of items ingested since creation."""
        return self._next_rank + len(self._storage)

    @property
    def remaining(self) -> int:
        """Number of items waiting to be extracted."""
        return len(self._storage)

    def _store(self, item: str) -> None:
        """Keep one converted item until it is extracted."""
        self._storage.append(item)

    @abstractmethod
    def validate(self, data: typing.Any) -> bool:
        """Tell whether this processor can ingest the given data."""

    @abstractmethod
    def ingest(self, data: typing.Any) -> None:
        """Process the data and store it piece by piece."""

    def output(self) -> tuple[int, str]:
        """Extract the oldest stored item along with its rank."""
        if len(self._storage) == 0:
            raise IndexError(f"{self._name} has no data left")
        rank = self._next_rank
        self._next_rank += 1
        return (rank, self._storage.pop(0))


def _is_number(value: typing.Any) -> bool:
    """True for int and float, but not for bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_log(value: typing.Any) -> bool:
    """True for a non-empty dict of string key-value pairs."""
    return (isinstance(value, dict) and len(value) > 0
            and all(isinstance(key, str) and isinstance(item, str)
                    for key, item in value.items()))


class NumericProcessor(DataProcessor):
    """Processes ints, floats and lists of them."""

    def __init__(self) -> None:
        super().__init__("Numeric Processor")

    def validate(self, data: typing.Any) -> bool:
        if _is_number(data):
            return True
        return (isinstance(data, list) and len(data) > 0
                and all(_is_number(item) for item in data))

    def ingest(self, data: int | float | list[int | float]) -> None:
        if not self.validate(data):
            raise TypeError("Improper numeric data")
        items = data if isinstance(data, list) else [data]
        for item in items:
            self._store(str(item))


class TextProcessor(DataProcessor):
    """Processes strings and lists of strings."""

    def __init__(self) -> None:
        super().__init__("Text Processor")

    def validate(self, data: typing.Any) -> bool:
        if isinstance(data, str):
            return True
        return (isinstance(data, list) and len(data) > 0
                and all(isinstance(item, str) for item in data))

    def ingest(self, data: str | list[str]) -> None:
        if not self.validate(data):
            raise TypeError("Improper text data")
        items = data if isinstance(data, list) else [data]
        for item in items:
            self._store(item)


class LogProcessor(DataProcessor):
    """Processes dicts of strings and lists of such dicts."""

    def __init__(self) -> None:
        super().__init__("Log Processor")

    def validate(self, data: typing.Any) -> bool:
        if _is_log(data):
            return True
        return (isinstance(data, list) and len(data) > 0
                and all(_is_log(item) for item in data))

    def ingest(self, data: dict[str, str] | list[dict[str, str]]) -> None:
        if not self.validate(data):
            raise TypeError("Improper log data")
        items = data if isinstance(data, list) else [data]
        for item in items:
            self._store(": ".join(item.values()))


class DataStream:
    """Routes every element of a stream to a matching processor."""

    def __init__(self) -> None:
        self._processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        """Add a processor to the routing list."""
        self._processors.append(proc)

    def process_stream(self, stream: list[typing.Any]) -> None:
        """Send each element to the first processor that accepts it."""
        for element in stream:
            for proc in self._processors:
                if proc.validate(element):
                    try:
                        proc.ingest(element)
                    except (TypeError, ValueError) as error:
                        print(f"DataStream error - {proc.name}: {error}")
                    break
            else:
                print("DataStream error - Can't process element in stream: "
                      f"{element}")

    def print_processors_stats(self) -> None:
        """Print how much data each processor handled and still holds."""
        print("== DataStream statistics ==")
        if len(self._processors) == 0:
            print("No processor found, no data")
            return
        for proc in self._processors:
            print(f"{proc.name}: total {proc.total} items processed, "
                  f"remaining {proc.remaining} on processor")


def consume(processor: DataProcessor, count: int) -> None:
    """Extract count items from a processor, ignoring exhaustion."""
    for _ in range(count):
        try:
            processor.output()
        except IndexError:
            return


def main() -> None:
    """Run the stream processing scenario."""
    print("=== Code Nexus - Data Stream ===")
    print()
    print("Initialize Data Stream...")
    stream = DataStream()
    stream.print_processors_stats()
    print()

    print("Registering Numeric Processor")
    numeric = NumericProcessor()
    stream.register_processor(numeric)
    print()

    batch: list[typing.Any] = [
        "Hello world",
        [3.14, -1, 2.71],
        [{"log_level": "WARNING",
          "log_message": "Telnet access! Use ssh instead"},
         {"log_level": "INFO", "log_message": "User wil is connected"}],
        42,
        ["Hi", "five"],
    ]
    print(f"Send first batch of data on stream: {batch}")
    stream.process_stream(batch)
    stream.print_processors_stats()
    print()

    print("Registering other data processors")
    text = TextProcessor()
    log = LogProcessor()
    stream.register_processor(text)
    stream.register_processor(log)
    print("Send the same batch again")
    stream.process_stream(batch)
    stream.print_processors_stats()
    print()

    print("Consume some elements from the data processors: "
          "Numeric 3, Text 2, Log 1")
    consume(numeric, 3)
    consume(text, 2)
    consume(log, 1)
    stream.print_processors_stats()


if __name__ == "__main__":
    main()
