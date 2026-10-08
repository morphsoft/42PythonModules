import sys


def parse_scores(arguments: list[str]) -> list[int]:
    """Convert the arguments to ints, discarding the invalid ones."""
    scores: list[int] = []
    for argument in arguments:
        try:
            scores.append(int(argument))
        except ValueError:
            print(f"Invalid parameter: '{argument}'")
    return scores


def main() -> None:
    """Compute basic statistics on the scores given as parameters."""
    print("=== Player Score Analytics ===")
    scores = parse_scores(sys.argv[1:])
    if len(scores) == 0:
        print("No scores provided. Usage: "
              "python3 ft_score_analytics.py <score1> <score2> ...")
        return
    total = sum(scores)
    high = max(scores)
    low = min(scores)
    print(f"Scores processed: {scores}")
    print(f"Total players: {len(scores)}")
    print(f"Total score: {total}")
    print(f"Average score: {total / len(scores)}")
    print(f"High score: {high}")
    print(f"Low score: {low}")
    print(f"Score range: {high - low}")


if __name__ == "__main__":
    main()
