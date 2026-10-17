import pytest


@pytest.mark.skip(
    reason="Pending implementation of the CLI-only --delete workflow"
)
def test_delete_flag_requires_confirmation_and_uses_warning_text():
    """Specify the future irreversible-delete confirmation contract."""
    expected_warning = (
        "Erase all metadata from file/s, this action is irreversible"
    )
    assert expected_warning


@pytest.mark.skip(
    reason="Pending implementation of the CLI-only --delete workflow"
)
def test_delete_flag_cancellation_preserves_all_files():
    """Cancellation must not call delete_all_metadata or alter files."""
    assert True


@pytest.mark.skip(
    reason="Pending implementation of the CLI-only --delete workflow"
)
def test_delete_flag_deletes_every_selected_file_but_not_gui_mode():
    """Confirmed CLI deletion must be per-file and excluded from GUI mode."""
    assert True
