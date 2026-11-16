"""Operator clean-up tool: list / reset-password / delete accounts."""
from unittest.mock import MagicMock, patch

import bcrypt

from app.tools import users as tool
from tests.conftest import FAKE_USER


def test_list_prints_accounts(capsys):
    db = MagicMock()
    doc = MagicMock(id="u1")
    doc.to_dict.return_value = {"email": "test@example.com"}
    db.collection.return_value.get.return_value = [doc]
    with patch.object(tool, "_projects_of", return_value=2):
        assert tool.cmd_list(db) == 0
    out = capsys.readouterr().out
    assert "test@example.com" in out and "1 account(s)" in out


def test_reset_password_sets_new_hash_and_signs_out(monkeypatch):
    db = MagicMock()
    session = MagicMock()
    db.collection.return_value.where.return_value.get.return_value = [session]
    answers = iter(["new-password-1", "new-password-1"])
    monkeypatch.setattr(tool.getpass, "getpass", lambda prompt="": next(answers))
    with patch.object(tool.auth_service, "get_user_by_email", return_value=FAKE_USER), \
         patch.object(tool.auth_service, "_write_audit") as audit:
        assert tool.cmd_reset_password(db, "TEST@example.com") == 0
    new_hash = db.collection.return_value.document.return_value.update.call_args.args[0]["password_hash"]
    assert bcrypt.checkpw(b"new-password-1", new_hash.encode())
    session.reference.delete.assert_called_once()
    assert audit.call_args.kwargs["action"] == "password_reset_by_operator"


def test_reset_password_unknown_email(capsys):
    with patch.object(tool.auth_service, "get_user_by_email", return_value=None):
        assert tool.cmd_reset_password(MagicMock(), "nobody@x.com") == 1
    assert "No account" in capsys.readouterr().out


def test_delete_needs_typed_confirmation(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "wrong@example.com")
    with patch.object(tool.auth_service, "get_user_by_email", return_value=FAKE_USER), \
         patch.object(tool, "_projects_of", return_value=1), \
         patch.object(tool.auth_service, "delete_account") as delete:
        assert tool.cmd_delete(MagicMock(), "test@example.com") == 1
    delete.assert_not_called()


def test_delete_confirmed(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "test@example.com")
    with patch.object(tool.auth_service, "get_user_by_email", return_value=FAKE_USER), \
         patch.object(tool, "_projects_of", return_value=1), \
         patch.object(tool.auth_service, "delete_account") as delete:
        assert tool.cmd_delete(MagicMock(), "test@example.com") == 0
    delete.assert_called_once_with(delete.call_args.args[0], "u1")


def test_unknown_command_prints_help(capsys):
    assert tool.main(["nonsense"]) == 1
    assert "reset-password" in capsys.readouterr().out
