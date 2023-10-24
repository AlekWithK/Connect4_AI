from io import TextIOWrapper
from pathlib import Path 
import subprocess
from time import sleep
from typing import Callable, Iterable, List, NamedTuple, TypeVar


class ExperimentStats(NamedTuple):
    player1: str
    player2: str
    player1_wins: int
    ties: int
    player2_wins: int

    def __repr__(self) -> str:
        return "\t".join(
            str(item)
            for item in [
                f"{self.player1} vs {self.player2}:",
                self.player1_wins,
                self.ties,
                self.player2_wins,
            ]
        )

    def write_to(self, f: TextIOWrapper) -> None:
        f.write(str(self))
        f.write("\n")


__T = TypeVar("__T")


def run_subprocesses(
    iterable: Iterable[__T],
    subprocess_creator: Callable[[__T], subprocess.Popen],
    max_concurrency: int,
) -> None:
    processes: List[subprocess.Popen] = []

    for input in iterable:
        if len(processes) >= max_concurrency:
            process = processes.pop(0)
            process.wait()

        processes.append(subprocess_creator(input))
        sleep(2)

    for process in processes:
        process.wait()


def read_last_line(file_path: Path) -> str:
    with open(file_path) as f:
        for line in f:
            pass
        return line


def read_last_7_lines(file_path: Path) -> str:
    with open(file_path) as f:
        return "".join(f.readlines()[-7:])


def run_experiments(
    p1: str, p2: str, seed_range: range, out_dir: Path
) -> ExperimentStats:
    out_dir.mkdir()

    f_final_board_states = open(
        out_dir.joinpath(f"{p1}-vs-{p2}-final-board-states.txt"), "w"
    )

    run_subprocesses(
        seed_range,
        lambda i: subprocess.Popen(
            f'python main.py -p1 {p1} -p2 {p2} -limit_players="1,2" -seed {i} -visualize False',
            shell=True,
            stdout=open(out_dir.joinpath(f"{i}.output"), "w"),
        ),
        5,
    )

    player1_wins = 0
    player2_wins = 0
    ties = 0

    for i in seed_range:
        f_final_board_states.write(f"{p1} vs {p2}, seed = {i}:\n")
        f_final_board_states.write(read_last_7_lines(out_dir.joinpath(f"{i}.output")))
        f_final_board_states.write("\n")

        last_line = read_last_line(out_dir.joinpath(f"{i}.output"))
        if "Player  1  has won" in last_line:
            player1_wins += 1
        elif "Player  2  has won" in last_line:
            player2_wins += 1
        else:
            ties += 1

    f_final_board_states.close()

    stats = ExperimentStats(p1, p2, player1_wins, ties, player2_wins)

    print(stats)

    return stats


def eval_for_submission(out_root_dir: Path) -> None:
    out_root_dir.mkdir()

    with open(out_root_dir.joinpath("stats.txt"), "w") as f:
        run_experiments(
            "alphaBetaAI",
            "stupidAI",
            range(1, 6),
            out_root_dir.joinpath("ab-vs-stupid"),
        ).write_to(f)

        run_experiments(
            "stupidAI",
            "alphaBetaAI",
            range(1, 6),
            out_root_dir.joinpath("stupid-vs-ab"),
        ).write_to(f)

        run_experiments(
            "alphaBetaAI",
            "randomAI",
            range(1, 6),
            out_root_dir.joinpath("ab-vs-random"),
        ).write_to(f)

        run_experiments(
            "randomAI",
            "alphaBetaAI",
            range(1, 6),
            out_root_dir.joinpath("random-vs-ab"),
        ).write_to(f)

        run_experiments(
            "alphaBetaAI",
            "monteCarloAI",
            range(1, 11),
            out_root_dir.joinpath("ab-vs-mc"),
        ).write_to(f)

        run_experiments(
            "monteCarloAI",
            "alphaBetaAI",
            range(1, 11),
            out_root_dir.joinpath("mc-vs-ab"),
        ).write_to(f)


def main() -> None:
    eval_for_submission(Path("outputs-test"))


if __name__ == "__main__":
    main()