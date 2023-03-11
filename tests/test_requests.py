from pathlib import Path

from uron import Uron


def test_requests():
    result = Uron(
        interpreter="python",
        requirements_file="requirements.txt",
        target_pkg="requests",
        pkg_versions=["2.28.0", "2.28.1", "2.28.2"],
        output="./result.json",
    ).execute(Path(__file__).parent / "template.py")

    assert result == [
        [{"version": "2.28.0"}, {"version": "2.28.1"}, {"version": "2.28.2"}]
    ]
