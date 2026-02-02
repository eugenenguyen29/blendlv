"""Tests for object panel conditional UI.

Tests TRIVESTA_PT_object_panel conditional UI for NPC dialog
and Interactive script_id based on entity_type.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestObjectPanelPoll:
    """Tests for TRIVESTA_PT_object_panel.poll()."""

    def test_poll_allows_mesh_object(self, mock_bpy_module: MagicMock) -> None:
        """Should show panel for MESH objects (existing behavior)."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_ctx = MagicMock()
        mock_ctx.object = MagicMock()
        mock_ctx.object.type = "MESH"

        assert TRIVESTA_PT_object_panel.poll(mock_ctx) is True

    def test_poll_allows_collection_instance(self, mock_bpy_module: MagicMock) -> None:
        """Should show panel for collection instances (new behavior)."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_ctx = MagicMock()
        mock_ctx.object = MagicMock()
        mock_ctx.object.type = "EMPTY"
        mock_ctx.object.instance_type = "COLLECTION"

        assert TRIVESTA_PT_object_panel.poll(mock_ctx) is True

    def test_poll_rejects_empty_without_collection(self, mock_bpy_module: MagicMock) -> None:
        """Should reject plain EMPTY objects."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_ctx = MagicMock()
        mock_ctx.object = MagicMock()
        mock_ctx.object.type = "EMPTY"
        mock_ctx.object.instance_type = "NONE"

        assert TRIVESTA_PT_object_panel.poll(mock_ctx) is False

    def test_poll_rejects_other_object_types(self, mock_bpy_module: MagicMock) -> None:
        """Should reject CAMERA, LIGHT, and other non-supported types."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        for obj_type in ["CAMERA", "LIGHT", "CURVE", "ARMATURE"]:
            mock_ctx = MagicMock()
            mock_ctx.object = MagicMock()
            mock_ctx.object.type = obj_type

            assert TRIVESTA_PT_object_panel.poll(mock_ctx) is False

    def test_poll_rejects_none_object(self, mock_bpy_module: MagicMock) -> None:
        """Should reject when no object is selected."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_ctx = MagicMock()
        mock_ctx.object = None

        assert TRIVESTA_PT_object_panel.poll(mock_ctx) is False


class TestDialogUIList:
    """Tests for TRIVESTA_UL_dialog_list UIList."""

    def test_dialog_list_has_bl_idname(self, mock_bpy_module: MagicMock) -> None:
        """Should have correct bl_idname for template_list."""
        from blender_extension.operators.dialog import TRIVESTA_UL_dialog_list

        assert TRIVESTA_UL_dialog_list.bl_idname == "TRIVESTA_UL_dialog_list"

    def test_dialog_list_draw_item_default_layout(self, mock_bpy_module: MagicMock) -> None:
        """Should render speaker and text in default layout."""
        from blender_extension.operators.dialog import TRIVESTA_UL_dialog_list

        # Setup mocks
        mock_context = MagicMock()
        mock_layout = MagicMock()
        mock_row = MagicMock()
        mock_layout.row.return_value = mock_row
        mock_data = MagicMock()
        mock_item = MagicMock()
        mock_item.speaker = "Alice"
        mock_item.text = "Hello, how are you?"

        # Create UIList and set layout_type
        uilist = TRIVESTA_UL_dialog_list()
        uilist.layout_type = "DEFAULT"

        # Execute
        uilist.draw_item(
            mock_context,
            mock_layout,
            mock_data,
            mock_item,
            icon=0,
            active_data=MagicMock(),
            active_property="dialog_line_index",
            index=0,
            flt_flag=0,
        )

        # Verify row was created and labels added
        mock_layout.row.assert_called_once_with(align=True)
        assert mock_row.label.call_count == 2
        # First label is speaker with USER icon
        mock_row.label.assert_any_call(text="Alice", icon="USER")
        # Second label is text
        mock_row.label.assert_any_call(text="Hello, how are you?")

    def test_dialog_list_draw_item_compact_layout(self, mock_bpy_module: MagicMock) -> None:
        """Should render in compact layout same as default."""
        from blender_extension.operators.dialog import TRIVESTA_UL_dialog_list

        mock_context = MagicMock()
        mock_layout = MagicMock()
        mock_row = MagicMock()
        mock_layout.row.return_value = mock_row
        mock_item = MagicMock()
        mock_item.speaker = "Bob"
        mock_item.text = "Short text"

        uilist = TRIVESTA_UL_dialog_list()
        uilist.layout_type = "COMPACT"

        uilist.draw_item(
            mock_context,
            mock_layout,
            MagicMock(),
            mock_item,
            icon=0,
            active_data=MagicMock(),
            active_property="",
            index=0,
            flt_flag=0,
        )

        mock_layout.row.assert_called_once_with(align=True)
        assert mock_row.label.call_count == 2

    def test_dialog_list_draw_item_grid_layout(self, mock_bpy_module: MagicMock) -> None:
        """Should render minimal grid icon layout."""
        from blender_extension.operators.dialog import TRIVESTA_UL_dialog_list

        mock_context = MagicMock()
        mock_layout = MagicMock()
        mock_item = MagicMock()
        mock_item.speaker = "Grid Speaker"
        mock_item.text = "Grid text"

        uilist = TRIVESTA_UL_dialog_list()
        uilist.layout_type = "GRID"

        uilist.draw_item(
            mock_context,
            mock_layout,
            MagicMock(),
            mock_item,
            icon=0,
            active_data=MagicMock(),
            active_property="",
            index=0,
            flt_flag=0,
        )

        # Grid layout shows just an icon
        mock_layout.label.assert_called_once_with(text="", icon="TEXT")

    def test_dialog_list_truncates_long_text(self, mock_bpy_module: MagicMock) -> None:
        """Should truncate text longer than 40 characters."""
        from blender_extension.operators.dialog import TRIVESTA_UL_dialog_list

        mock_context = MagicMock()
        mock_layout = MagicMock()
        mock_row = MagicMock()
        mock_layout.row.return_value = mock_row
        mock_item = MagicMock()
        mock_item.speaker = "Long"
        # 50 character text
        mock_item.text = "A" * 50

        uilist = TRIVESTA_UL_dialog_list()
        uilist.layout_type = "DEFAULT"

        uilist.draw_item(
            mock_context,
            mock_layout,
            MagicMock(),
            mock_item,
            icon=0,
            active_data=MagicMock(),
            active_property="",
            index=0,
            flt_flag=0,
        )

        # Check that truncated text was passed (first 40 chars + "...")
        expected_text = "A" * 40 + "..."
        mock_row.label.assert_any_call(text=expected_text)

    def test_dialog_list_handles_empty_speaker(self, mock_bpy_module: MagicMock) -> None:
        """Should show placeholder when speaker is empty."""
        from blender_extension.operators.dialog import TRIVESTA_UL_dialog_list

        mock_context = MagicMock()
        mock_layout = MagicMock()
        mock_row = MagicMock()
        mock_layout.row.return_value = mock_row
        mock_item = MagicMock()
        mock_item.speaker = ""
        mock_item.text = "Some text"

        uilist = TRIVESTA_UL_dialog_list()
        uilist.layout_type = "DEFAULT"

        uilist.draw_item(
            mock_context,
            mock_layout,
            MagicMock(),
            mock_item,
            icon=0,
            active_data=MagicMock(),
            active_property="",
            index=0,
            flt_flag=0,
        )

        mock_row.label.assert_any_call(text="(No speaker)", icon="USER")

    def test_dialog_list_handles_empty_text(self, mock_bpy_module: MagicMock) -> None:
        """Should show placeholder when text is empty."""
        from blender_extension.operators.dialog import TRIVESTA_UL_dialog_list

        mock_context = MagicMock()
        mock_layout = MagicMock()
        mock_row = MagicMock()
        mock_layout.row.return_value = mock_row
        mock_item = MagicMock()
        mock_item.speaker = "Speaker"
        mock_item.text = ""

        uilist = TRIVESTA_UL_dialog_list()
        uilist.layout_type = "DEFAULT"

        uilist.draw_item(
            mock_context,
            mock_layout,
            MagicMock(),
            mock_item,
            icon=0,
            active_data=MagicMock(),
            active_property="",
            index=0,
            flt_flag=0,
        )

        mock_row.label.assert_any_call(text="(Empty)")


class TestObjectPanelConditionalUI:
    """Tests for conditional UI in object panel."""

    def _create_mock_context_and_layout(
        self, entity_type: str
    ) -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
        """Create mock context, layout, and box for panel tests.

        Returns:
            Tuple of (mock_context, mock_layout, mock_box, mock_col).
        """
        mock_context = MagicMock()
        mock_settings = MagicMock()
        mock_settings.entity_type = entity_type
        mock_context.object.trivesta = mock_settings
        # Set library to None so get_library_source returns None
        mock_context.object.library = None

        mock_layout = MagicMock()
        mock_box = MagicMock()
        mock_row = MagicMock()
        mock_col = MagicMock()
        mock_layout.box.return_value = mock_box
        mock_layout.row.return_value = mock_row
        mock_box.row.return_value = mock_row
        mock_row.column.return_value = mock_col

        return mock_context, mock_layout, mock_box, mock_col

    @patch("blender_extension.panels.object.get_library_source", return_value=None)
    def test_panel_shows_dialog_ui_for_npc(
        self, mock_get_lib: MagicMock, mock_bpy_module: MagicMock
    ) -> None:
        """Should show dialog box when entity_type is 'npc'."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_context, mock_layout, mock_box, _ = self._create_mock_context_and_layout("npc")

        panel = TRIVESTA_PT_object_panel()
        panel.layout = mock_layout
        panel.draw(mock_context)

        # Verify dialog box was created with correct label
        # Check that box.label was called with NPC Dialog
        label_calls = [c for c in mock_box.label.call_args_list]
        npc_label_calls = [c for c in label_calls if c[1].get("text") == "NPC Dialog"]
        assert len(npc_label_calls) == 1
        assert npc_label_calls[0][1].get("icon") == "TEXT"

    @patch("blender_extension.panels.object.get_library_source", return_value=None)
    def test_panel_shows_script_id_for_interactive(
        self, mock_get_lib: MagicMock, mock_bpy_module: MagicMock
    ) -> None:
        """Should show script_id field when entity_type is 'interactive'."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_context, mock_layout, mock_box, _ = self._create_mock_context_and_layout("interactive")

        panel = TRIVESTA_PT_object_panel()
        panel.layout = mock_layout
        panel.draw(mock_context)

        # Verify Interactive box label
        label_calls = [c for c in mock_box.label.call_args_list]
        script_label_calls = [c for c in label_calls if c[1].get("text") == "Interactive Scripting"]
        assert len(script_label_calls) == 1
        assert script_label_calls[0][1].get("icon") == "SCRIPT"

        # Verify script_id prop was added
        prop_calls = [c for c in mock_box.prop.call_args_list]
        script_prop_calls = [c for c in prop_calls if len(c[0]) >= 2 and c[0][1] == "script_id"]
        assert len(script_prop_calls) == 1

    @patch("blender_extension.panels.object.get_library_source", return_value=None)
    def test_panel_hides_dialog_for_non_npc(
        self, mock_get_lib: MagicMock, mock_bpy_module: MagicMock
    ) -> None:
        """Should not show dialog box for static entity type."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_context, mock_layout, mock_box, _ = self._create_mock_context_and_layout("static")

        panel = TRIVESTA_PT_object_panel()
        panel.layout = mock_layout
        panel.draw(mock_context)

        # Verify NPC Dialog label was NOT added
        label_calls = [c for c in mock_box.label.call_args_list]
        npc_label_calls = [c for c in label_calls if c[1].get("text") == "NPC Dialog"]
        assert len(npc_label_calls) == 0

        # Verify template_list was not called
        mock_row = mock_box.row.return_value
        mock_row.template_list.assert_not_called()

    @patch("blender_extension.panels.object.get_library_source", return_value=None)
    def test_panel_shows_add_remove_buttons(
        self, mock_get_lib: MagicMock, mock_bpy_module: MagicMock
    ) -> None:
        """Should show add/remove operator buttons for NPC dialog."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_context, mock_layout, mock_box, mock_col = self._create_mock_context_and_layout("npc")

        panel = TRIVESTA_PT_object_panel()
        panel.layout = mock_layout
        panel.draw(mock_context)

        # Check that operator calls include add and remove
        operator_calls = [c for c in mock_col.operator.call_args_list]
        operator_ids = [c[0][0] for c in operator_calls]
        assert "trivesta.add_dialog_line" in operator_ids
        assert "trivesta.remove_dialog_line" in operator_ids

    @patch("blender_extension.panels.object.get_library_source", return_value=None)
    def test_panel_shows_move_buttons(
        self, mock_get_lib: MagicMock, mock_bpy_module: MagicMock
    ) -> None:
        """Should show move up/down buttons for NPC dialog."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_context, mock_layout, mock_box, mock_col = self._create_mock_context_and_layout("npc")

        panel = TRIVESTA_PT_object_panel()
        panel.layout = mock_layout
        panel.draw(mock_context)

        # Check for move operator calls (should be 2 - up and down)
        operator_calls = [c for c in mock_col.operator.call_args_list]
        move_calls = [c for c in operator_calls if c[0][0] == "trivesta.move_dialog_line"]
        assert len(move_calls) == 2

    @patch("blender_extension.panels.object.get_library_source", return_value=None)
    def test_panel_shows_edit_dialog_button(
        self, mock_get_lib: MagicMock, mock_bpy_module: MagicMock
    ) -> None:
        """Should show Edit Dialog button for NPC entity type."""
        from blender_extension.panels.object import TRIVESTA_PT_object_panel

        mock_context, mock_layout, mock_box, _ = self._create_mock_context_and_layout("npc")

        panel = TRIVESTA_PT_object_panel()
        panel.layout = mock_layout
        panel.draw(mock_context)

        # Verify edit_dialog operator was called
        operator_calls = [c for c in mock_box.operator.call_args_list]
        edit_calls = [c for c in operator_calls if c[0][0] == "trivesta.edit_dialog"]
        assert len(edit_calls) == 1
        assert edit_calls[0][1].get("text") == "Edit Dialog"
        assert edit_calls[0][1].get("icon") == "GREASEPENCIL"


class TestUIListRegistration:
    """Tests for UIList registration."""

    def test_uilist_in_classes_list(self, mock_bpy_module: MagicMock) -> None:
        """UIList should be in the classes list for registration."""
        from blender_extension.core.registry import collect_classes

        classes = collect_classes()
        class_names = [cls.__name__ for cls in classes if hasattr(cls, "__name__")]

        assert "TRIVESTA_UL_dialog_list" in class_names
