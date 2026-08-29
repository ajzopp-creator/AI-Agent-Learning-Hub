"""Regression tests for cli.py argument parsing and flag dispatch."""

from cli import build_parser


def test_cli_parser_defaults() -> None:
    """Ensure parser initializes with default flags set to False/None."""
    parser = build_parser()
    args = parser.parse_args([])
    assert args.smoke is False
    assert args.bench is False
    assert args.prompt is None


def test_cli_parser_prompt_argument() -> None:
    """Ensure --prompt accepts string arguments without callable errors."""
    parser = build_parser()
    args = parser.parse_args(["--prompt", "Test prompt text"])
    assert args.prompt == "Test prompt text"
    assert args.smoke is False
    assert args.bench is False


def test_cli_parser_flags() -> None:
    """Ensure --smoke and --bench flags parse properly."""
    parser = build_parser()
    args_smoke = parser.parse_args(["--smoke"])
    assert args_smoke.smoke is True

    args_bench = parser.parse_args(["--bench"])
    assert args_bench.bench is True