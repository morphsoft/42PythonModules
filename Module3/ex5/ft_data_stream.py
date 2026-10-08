import random
import typing

PLAYERS = ["alice", "bob", "charlie", "dylan"]
ACTIONS = ["run", "eat", "sleep", "grab", "move", "climb", "swim",
           "use", "release"]

Event = tuple[str, str]


def gen_event() -> typing.Generator[Event, None, None]:
    """Endlessly yield random (player, action) events."""
    while True:
        yield (random.choice(PLAYERS), random.choice(ACTIONS))


def consume_event(events: list[Event]) -> typing.Generator[Event, None, None]:
    """Yield random events removed from the list until it is empty."""
    while len(events) > 0:
        yield events.pop(random.randrange(len(events)))


def main() -> None:
    """Stream events from generators and consume a list of them."""
    print("=== Game Data Stream Processor ===")
    stream = gen_event()
    for index in range(1000):
        name, action = next(stream)
        print(f"Event {index}: Player {name} did action {action}")

    event_list: list[Event] = []
    for _ in range(10):
        event_list.append(next(stream))
    print(f"Built list of {len(event_list)} events: {event_list}")

    for event in consume_event(event_list):
        print(f"Got event from list: {event}")
        print(f"Remains in list: {event_list}")


if __name__ == "__main__":
    main()
