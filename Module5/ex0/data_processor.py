from abc import ABC, abstractmethod
from typing import Any


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
    def validate(self, data: Any) -> bool:
        """Tell whether this processor can ingest the given data."""

    @abstractmethod
    def ingest(self, data: Any) -> None:
        """Process the data and store it piece by piece."""

    def output(self) -> tuple[int, str]:
        """Extract the oldest stored item along with its rank."""
        if len(self._storage) == 0:
            raise IndexError(f"{self._name} has no data left")
        rank = self._next_rank
        self._next_rank += 1
        return (rank, self._storage.pop(0))


def _is_number(value: Any) -> bool:
    """True for int and float, but not for bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_log(value: Any) -> bool:
    """True for a non-empty dict of string key-value pairs."""
    return (isinstance(value, dict) and len(value) > 0
            and all(isinstance(key, str) and isinstance(item, str)
                    for key, item in value.items()))


class NumericProcessor(DataProcessor):
    """Processes ints, floats and lists of them."""

    def __init__(self) -> None:
        super().__init__("Numeric Processor")

    def validate(self, data: Any) -> bool:
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

    def validate(self, data: Any) -> bool:
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

    def validate(self, data: Any) -> bool:
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


def extract(processor: DataProcessor, count: int, label: str) -> None:
    """Extract count items from the processor and print them."""
    plural = "s" if count != 1 else ""
    print(f"Extracting {count} value{plural}...")
    for _ in range(count):
        try:
            rank, value = processor.output()
        except IndexError as error:
            print(f"Got exception: {error}")
            return
        print(f"{label} {rank}: {value}")


def main() -> None:
    """Exercise each processor with valid and invalid data."""
    print("=== Code Nexus - Data Processor ===")
    print()

    print("Testing Numeric Processor...")
    numeric = NumericProcessor()
    print(f"Trying to validate input '42': {numeric.validate(42)}")
    print(f"Trying to validate input 'Hello': {numeric.validate('Hello')}")
    print("Test invalid ingestion of string 'foo' without prior validation:")
    try:
        numeric.ingest("foo")
    except TypeError as error:
        print(f"Got exception: {error}")
    numbers: list[int | float] = [1, 2, 3, 4, 5]
    print(f"Processing data: {numbers}")
    numeric.ingest(numbers)
    extract(numeric, 3, "Numeric value")
    print()

    print("Testing Text Processor...")
    text = TextProcessor()
    print(f"Trying to validate input '42': {text.validate(42)}")
    words = ["Hello", "Nexus", "World"]
    print(f"Processing data: {words}")
    text.ingest(words)
    extract(text, 1, "Text value")
    print()

    print("Testing Log Processor...")
    log = LogProcessor()
    print(f"Trying to validate input 'Hello': {log.validate('Hello')}")
    logs = [
        {"log_level": "NOTICE", "log_message": "Connection to server"},
        {"log_level": "ERROR", "log_message": "Unauthorized access!!"},
    ]
    print(f"Processing data: {logs}")
    log.ingest(logs)
    extract(log, 2, "Log entry")


if __name__ == "__main__":
    main()
