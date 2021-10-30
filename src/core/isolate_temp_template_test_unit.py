import pytest

from .isolate_temp_template import get_relative_path


@pytest.mark.parametrize(
    "f_path, cur_dir, dest_dir, expected",
    [
        (
            "/dir_11/dir_12/dir_13",
            "/dir_11",
            "/dir_11/dir_14",
            "/dir_11/dir_14/dir_12/dir_13",
        )
    ],
)
def test_get_relative_path(
    f_path: str, cur_dir: str, dest_dir: str, expected: str
) -> None:
    assert (
        get_relative_path(f_path=f_path, cur_dir=cur_dir, dest_dir=dest_dir) == expected
    )
