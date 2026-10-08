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


class ExportPlugin(typing.Protocol):
    """Anything with a process_output method can export data."""

    def process_output(self, data: list[tuple[int, str]]) -> None:
        """Export the (rank, value) pairs extracted from a processor."""


class CSVExportPlugin:
    """Exports values as one line of comma-separated fields."""

    @staticmethod
    def _escape(value: str) -> str:
        if "," in value or '"' in value or "\n" in value:
            return '"' + value.replace('"', '""') + '"'
        return value

    def process_output(self, data: list[tuple[int, str]]) -> None:
        print("CSV Output:")
        print(",".join(self._escape(value) for _, value in data))


class JSONExportPlugin:
    """Exports values as a JSON object keyed by item rank."""

    @staticmethod
    def _escape(value: str) -> str:
        return (value.replace("\\", "\\\\").replace('"', '\\"')
                .replace("\n", "\\n"))

    def process_output(self, data: list[tuple[int, str]]) -> None:
        print("JSON Output:")
        fields = [f'"item_{rank}": "{self._escape(value)}"'
                  for rank, value in data]
        print("{" + ", ".join(fields) + "}")


class DataStream:
    """Routes a stream to processors and exports their output."""

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

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        """Consume up to nb items per processor and export them."""
        for proc in self._processors:
            data: list[tuple[int, str]] = []
            for _ in range(nb):
                try:
                    data.append(proc.output())
                except IndexError:
                    break
            if len(data) > 0:
                plugin.process_output(data)


def main() -> None:
    """Run the full pipeline scenario."""
    print("=== Code Nexus - Data Pipeline ===")
    print()
    print("Initialize Data Stream...")
    stream = DataStream()
    print()
    stream.print_processors_stats()
    print()

    print("Registering Processors")
    stream.register_processor(NumericProcessor())
    stream.register_processor(TextProcessor())
    stream.register_processor(LogProcessor())
    print()

    first_batch: list[typing.Any] = [
        "Hello world",
        [3.14, -1, 2.71],
        [{"log_level": "WARNING",
          "log_message": "Telnet access! Use ssh instead"},
         {"log_level": "INFO", "log_message": "User wil is connected"}],
        42,
        ["Hi", "five"],
    ]
    print(f"Send first batch of data on stream: {first_batch}")
    stream.process_stream(first_batch)
    print()
    stream.print_processors_stats()
    print()

    print("Send 3 processed data from each processor to a CSV plugin:")
    stream.output_pipeline(3, CSVExportPlugin())
    print()
    stream.print_processors_stats()
    print()

    second_batch: list[typing.Any] = [
        21,
        ["I love AI", "LLMs are wonderful", "Stay healthy"],
        [{"log_level": "ERROR", "log_message": "500 server crash"},
         {"log_level": "NOTICE",
          "log_message": "Certificate expires in 10 days"}],
        [32, 42, 64, 84, 128, 168],
        "World hello",
    ]
    print(f"Send another batch of data: {second_batch}")
    stream.process_stream(second_batch)
    print()
    stream.print_processors_stats()
    print()

    print("Send 5 processed data from each processor to a JSON plugin:")
    stream.output_pipeline(5, JSONExportPlugin())
    print()
    stream.print_processors_stats()


if __name__ == "__main__":
    main()
