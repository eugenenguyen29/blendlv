"""Tests for dialog management operators.

Tests TRIVESTA_OT_add_dialog_line, TRIVESTA_OT_remove_dialog_line,
and TRIVESTA_OT_move_dialog_line operators.
"""

from __future__ import annotations

from unittest.mock import MagicMock


class TestAddDialogLine:
    """Tests for TRIVESTA_OT_add_dialog_line operator."""

    def test_add_dialog_line_creates_item(self, mock_bpy_module: MagicMock) -> None:
        """Should add a new dialog line to the collection."""
        from blender_extension.operators.dialog import TRIVESTA_OT_add_dialog_line

        # Setup mock
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_item = MagicMock()
        mock_dialog_lines.add.return_value = mock_item
        mock_dialog_lines.__len__ = MagicMock(return_value=1)
        mock_settings.dialog_lines = mock_dialog_lines

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Execute
        op = TRIVESTA_OT_add_dialog_line()
        result = op.execute(mock_context)

        # Verify
        assert result == {"FINISHED"}
        mock_dialog_lines.add.assert_called_once()

    def test_add_dialog_line_sets_defaults(self, mock_bpy_module: MagicMock) -> None:
        """New line should have empty speaker and text defaults."""
        from blender_extension.operators.dialog import TRIVESTA_OT_add_dialog_line

        # Setup mock
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_item = MagicMock()
        mock_dialog_lines.add.return_value = mock_item
        mock_dialog_lines.__len__ = MagicMock(return_value=1)
        mock_settings.dialog_lines = mock_dialog_lines

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Execute
        op = TRIVESTA_OT_add_dialog_line()
        op.execute(mock_context)

        # Verify defaults were set
        assert mock_item.speaker == ""
        assert mock_item.text == ""

    def test_add_dialog_line_updates_index(self, mock_bpy_module: MagicMock) -> None:
        """Index should point to newly added item."""
        from blender_extension.operators.dialog import TRIVESTA_OT_add_dialog_line

        # Setup mock with existing items
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_item = MagicMock()
        mock_dialog_lines.add.return_value = mock_item
        mock_dialog_lines.__len__ = MagicMock(return_value=3)  # After add, 3 items
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 0

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Execute
        op = TRIVESTA_OT_add_dialog_line()
        op.execute(mock_context)

        # Verify index points to last item (index 2 for 3 items)
        assert mock_settings.dialog_line_index == 2

    def test_add_dialog_line_cancelled_without_object(self, mock_bpy_module: MagicMock) -> None:
        """Should return CANCELLED when no object selected."""
        from blender_extension.operators.dialog import TRIVESTA_OT_add_dialog_line

        mock_context = MagicMock()
        mock_context.object = None

        op = TRIVESTA_OT_add_dialog_line()
        result = op.execute(mock_context)

        assert result == {"CANCELLED"}


class TestRemoveDialogLine:
    """Tests for TRIVESTA_OT_remove_dialog_line operator."""

    def test_remove_dialog_line_deletes_item(self, mock_bpy_module: MagicMock) -> None:
        """Should remove selected dialog line from collection."""
        from blender_extension.operators.dialog import TRIVESTA_OT_remove_dialog_line

        # Setup mock
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=2)  # After remove, 2 items
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 1

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Execute
        op = TRIVESTA_OT_remove_dialog_line()
        result = op.execute(mock_context)

        # Verify
        assert result == {"FINISHED"}
        mock_dialog_lines.remove.assert_called_once_with(1)

    def test_remove_dialog_line_updates_index(self, mock_bpy_module: MagicMock) -> None:
        """Index should adjust after removal to stay in bounds."""
        from blender_extension.operators.dialog import TRIVESTA_OT_remove_dialog_line

        # Setup mock - removing last item
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=1)  # After remove, 1 item left
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 2  # Was pointing to item at index 2

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Execute
        op = TRIVESTA_OT_remove_dialog_line()
        op.execute(mock_context)

        # Index should clamp to valid range (0 for 1 item)
        assert mock_settings.dialog_line_index == 0

    def test_remove_dialog_line_poll_false_when_empty(self, mock_bpy_module: MagicMock) -> None:
        """Poll should return False when no dialog lines exist."""
        from blender_extension.operators.dialog import TRIVESTA_OT_remove_dialog_line

        # Setup mock with empty collection
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=0)
        mock_settings.dialog_lines = mock_dialog_lines

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Verify poll returns False
        result = TRIVESTA_OT_remove_dialog_line.poll(mock_context)
        assert result is False

    def test_remove_dialog_line_poll_true_when_has_items(self, mock_bpy_module: MagicMock) -> None:
        """Poll should return True when dialog lines exist."""
        from blender_extension.operators.dialog import TRIVESTA_OT_remove_dialog_line

        # Setup mock with items
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=2)
        mock_settings.dialog_lines = mock_dialog_lines

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Verify poll returns True
        result = TRIVESTA_OT_remove_dialog_line.poll(mock_context)
        assert result is True


class TestMoveDialogLine:
    """Tests for TRIVESTA_OT_move_dialog_line operator."""

    def test_move_dialog_line_up(self, mock_bpy_module: MagicMock) -> None:
        """Should move selected line up one position."""
        from blender_extension.operators.dialog import TRIVESTA_OT_move_dialog_line

        # Setup mock
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=3)
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 2  # Item at index 2

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Execute move up
        op = TRIVESTA_OT_move_dialog_line()
        op.direction = "UP"
        result = op.execute(mock_context)

        # Verify
        assert result == {"FINISHED"}
        mock_dialog_lines.move.assert_called_once_with(2, 1)
        assert mock_settings.dialog_line_index == 1

    def test_move_dialog_line_down(self, mock_bpy_module: MagicMock) -> None:
        """Should move selected line down one position."""
        from blender_extension.operators.dialog import TRIVESTA_OT_move_dialog_line

        # Setup mock
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=3)
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 0  # Item at index 0

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Execute move down
        op = TRIVESTA_OT_move_dialog_line()
        op.direction = "DOWN"
        result = op.execute(mock_context)

        # Verify
        assert result == {"FINISHED"}
        mock_dialog_lines.move.assert_called_once_with(0, 1)
        assert mock_settings.dialog_line_index == 1

    def test_move_dialog_line_clamps_at_top(self, mock_bpy_module: MagicMock) -> None:
        """Should not move beyond top of list."""
        from blender_extension.operators.dialog import TRIVESTA_OT_move_dialog_line

        # Setup mock - already at top
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=3)
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 0  # Already at top

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Execute move up (should not move)
        op = TRIVESTA_OT_move_dialog_line()
        op.direction = "UP"
        result = op.execute(mock_context)

        # Verify no move called (index unchanged)
        assert result == {"FINISHED"}
        mock_dialog_lines.move.assert_not_called()
        assert mock_settings.dialog_line_index == 0

    def test_move_dialog_line_clamps_at_bottom(self, mock_bpy_module: MagicMock) -> None:
        """Should not move beyond bottom of list."""
        from blender_extension.operators.dialog import TRIVESTA_OT_move_dialog_line

        # Setup mock - already at bottom
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=3)
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 2  # Already at bottom (0, 1, 2)

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Execute move down (should not move)
        op = TRIVESTA_OT_move_dialog_line()
        op.direction = "DOWN"
        result = op.execute(mock_context)

        # Verify no move called (index unchanged)
        assert result == {"FINISHED"}
        mock_dialog_lines.move.assert_not_called()
        assert mock_settings.dialog_line_index == 2

    def test_move_dialog_line_poll_false_when_empty(self, mock_bpy_module: MagicMock) -> None:
        """Poll should return False when no dialog lines exist."""
        from blender_extension.operators.dialog import TRIVESTA_OT_move_dialog_line

        # Setup mock with empty collection
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=0)
        mock_settings.dialog_lines = mock_dialog_lines

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Verify poll returns False
        result = TRIVESTA_OT_move_dialog_line.poll(mock_context)
        assert result is False


class TestEditDialogPopup:
    """Tests for TRIVESTA_OT_edit_dialog popup operator."""

    def test_edit_dialog_has_invoke_method(self, mock_bpy_module: MagicMock) -> None:
        """Should have invoke method for popup."""
        from blender_extension.operators.dialog import TRIVESTA_OT_edit_dialog

        assert hasattr(TRIVESTA_OT_edit_dialog, "invoke")
        assert callable(getattr(TRIVESTA_OT_edit_dialog, "invoke", None))

    def test_edit_dialog_invoke_returns_running_modal(self, mock_bpy_module: MagicMock) -> None:
        """Should call invoke_popup and return its result."""
        from blender_extension.operators.dialog import TRIVESTA_OT_edit_dialog

        mock_context = MagicMock()
        mock_context.window_manager.invoke_popup = MagicMock(return_value={"RUNNING_MODAL"})

        op = TRIVESTA_OT_edit_dialog()
        result = op.invoke(mock_context, MagicMock())

        mock_context.window_manager.invoke_popup.assert_called_once()
        # Verify width=500 was passed
        call_args = mock_context.window_manager.invoke_popup.call_args
        assert call_args[1].get("width") == 500
        assert result == {"RUNNING_MODAL"}

    def test_edit_dialog_has_draw_method(self, mock_bpy_module: MagicMock) -> None:
        """Should have draw method for popup UI."""
        from blender_extension.operators.dialog import TRIVESTA_OT_edit_dialog

        assert hasattr(TRIVESTA_OT_edit_dialog, "draw")
        assert callable(getattr(TRIVESTA_OT_edit_dialog, "draw", None))

    def test_edit_dialog_draw_shows_uilist(self, mock_bpy_module: MagicMock) -> None:
        """Should render template_list in draw()."""
        from blender_extension.operators.dialog import TRIVESTA_OT_edit_dialog

        # Setup mock context with object and settings
        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=2)
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 0

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Create operator and mock layout
        op = TRIVESTA_OT_edit_dialog()
        mock_layout = MagicMock()
        op.layout = mock_layout

        op.draw(mock_context)

        # Verify template_list was called
        # Check nested layout calls to find template_list
        template_list_called = False
        for call in mock_layout.method_calls:
            if "template_list" in str(call):
                template_list_called = True
                break
        # Also check box's calls
        for call in mock_layout.box.return_value.method_calls:
            if "template_list" in str(call):
                template_list_called = True
                break
        for call in mock_layout.box.return_value.row.return_value.method_calls:
            if "template_list" in str(call):
                template_list_called = True
                break

        assert template_list_called

    def test_edit_dialog_draw_shows_speaker_field(self, mock_bpy_module: MagicMock) -> None:
        """Should render speaker property field in draw()."""
        from blender_extension.operators.dialog import TRIVESTA_OT_edit_dialog

        # Setup mock context with object and dialog lines
        mock_line = MagicMock()
        mock_line.speaker = "NPC"
        mock_line.text = "Hello"

        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=1)
        mock_dialog_lines.__getitem__ = MagicMock(return_value=mock_line)
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 0

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Create operator and mock layout
        op = TRIVESTA_OT_edit_dialog()
        mock_layout = MagicMock()
        op.layout = mock_layout

        op.draw(mock_context)

        # Verify prop was called with speaker
        all_calls = str(mock_layout.method_calls)
        assert "speaker" in all_calls.lower() or any(
            "speaker" in str(call).lower() for call in mock_layout.box.return_value.method_calls
        )

    def test_edit_dialog_draw_shows_text_field(self, mock_bpy_module: MagicMock) -> None:
        """Should render text property field in draw()."""
        from blender_extension.operators.dialog import TRIVESTA_OT_edit_dialog

        # Setup mock context with object and dialog lines
        mock_line = MagicMock()
        mock_line.speaker = "NPC"
        mock_line.text = "Hello"

        mock_settings = MagicMock()
        mock_dialog_lines = MagicMock()
        mock_dialog_lines.__len__ = MagicMock(return_value=1)
        mock_dialog_lines.__getitem__ = MagicMock(return_value=mock_line)
        mock_settings.dialog_lines = mock_dialog_lines
        mock_settings.dialog_line_index = 0

        mock_obj = MagicMock()
        mock_obj.trivesta = mock_settings

        mock_context = MagicMock()
        mock_context.object = mock_obj

        # Create operator and mock layout
        op = TRIVESTA_OT_edit_dialog()
        mock_layout = MagicMock()
        op.layout = mock_layout

        op.draw(mock_context)

        # Verify prop was called with text
        all_calls = str(mock_layout.method_calls)
        assert "text" in all_calls.lower() or any(
            "text" in str(call).lower() for call in mock_layout.box.return_value.method_calls
        )

    def test_edit_dialog_execute_returns_finished(self, mock_bpy_module: MagicMock) -> None:
        """Should return FINISHED from execute."""
        from blender_extension.operators.dialog import TRIVESTA_OT_edit_dialog

        mock_context = MagicMock()
        op = TRIVESTA_OT_edit_dialog()
        result = op.execute(mock_context)

        assert result == {"FINISHED"}

    def test_edit_dialog_poll_requires_object(self, mock_bpy_module: MagicMock) -> None:
        """Should require active object with trivesta attribute."""
        from blender_extension.operators.dialog import TRIVESTA_OT_edit_dialog

        # No object
        mock_context = MagicMock()
        mock_context.object = None
        assert TRIVESTA_OT_edit_dialog.poll(mock_context) is False

        # Object without trivesta attribute
        mock_obj = MagicMock(spec=[])  # No trivesta attribute
        mock_context.object = mock_obj
        assert TRIVESTA_OT_edit_dialog.poll(mock_context) is False

        # Object with trivesta attribute
        mock_obj = MagicMock()
        mock_obj.trivesta = MagicMock()
        mock_context.object = mock_obj
        assert TRIVESTA_OT_edit_dialog.poll(mock_context) is True


class TestDialogOperatorRegistration:
    """Tests for dialog operator registration."""

    def test_operators_in_classes_list(self, mock_bpy_module: MagicMock) -> None:
        """Dialog operators should be in the classes list for registration."""
        from blender_extension.core.registry import collect_classes

        classes = collect_classes()
        class_names = [cls.__name__ for cls in classes if hasattr(cls, "__name__")]

        assert "TRIVESTA_OT_add_dialog_line" in class_names
        assert "TRIVESTA_OT_remove_dialog_line" in class_names
        assert "TRIVESTA_OT_move_dialog_line" in class_names
        assert "TRIVESTA_OT_edit_dialog" in class_names

    def test_operators_have_bl_idname(self, mock_bpy_module: MagicMock) -> None:
        """Operators should have correct bl_idname attributes."""
        from blender_extension.operators.dialog import (
            TRIVESTA_OT_add_dialog_line,
            TRIVESTA_OT_move_dialog_line,
            TRIVESTA_OT_remove_dialog_line,
        )

        assert TRIVESTA_OT_add_dialog_line.bl_idname == "trivesta.add_dialog_line"
        assert TRIVESTA_OT_remove_dialog_line.bl_idname == "trivesta.remove_dialog_line"
        assert TRIVESTA_OT_move_dialog_line.bl_idname == "trivesta.move_dialog_line"

    def test_operators_have_bl_options(self, mock_bpy_module: MagicMock) -> None:
        """Operators should have REGISTER and UNDO options."""
        from blender_extension.operators.dialog import (
            TRIVESTA_OT_add_dialog_line,
            TRIVESTA_OT_move_dialog_line,
            TRIVESTA_OT_remove_dialog_line,
        )

        assert "REGISTER" in TRIVESTA_OT_add_dialog_line.bl_options
        assert "UNDO" in TRIVESTA_OT_add_dialog_line.bl_options
        assert "REGISTER" in TRIVESTA_OT_remove_dialog_line.bl_options
        assert "UNDO" in TRIVESTA_OT_remove_dialog_line.bl_options
        assert "REGISTER" in TRIVESTA_OT_move_dialog_line.bl_options
        assert "UNDO" in TRIVESTA_OT_move_dialog_line.bl_options
