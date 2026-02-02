"""Tests for export operator.

Tests TRIVESTA_OT_export operator for exporting Trivesta Level data.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestTrivestaExportOperatorExecute:
    """Tests for TRIVESTA_OT_export.execute() method."""

    def test_execute_success(self, mock_bpy_module: MagicMock) -> None:
        """Should return FINISHED when export succeeds."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        mock_settings = MagicMock()
        mock_settings.export_path = "//exports/"

        mock_ctx = MagicMock()
        mock_ctx.scene.trivesta = mock_settings

        mock_bpy_module.path.abspath.return_value = "/abs/exports/"

        with patch("blender_extension.operators.export.export_world") as mock_export:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.message = "Export complete"
            mock_result.files_created = ["file1.glb"]
            mock_result.errors = []
            mock_export.return_value = mock_result

            op = TRIVESTA_OT_export()
            result = op.execute(mock_ctx)

            assert result == {"FINISHED"}
            mock_export.assert_called_once_with(mock_ctx, "/abs/exports/")

    def test_execute_no_export_path(self, mock_bpy_module: MagicMock) -> None:
        """Should return CANCELLED when export path is empty."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        mock_settings = MagicMock()
        mock_settings.export_path = ""

        mock_ctx = MagicMock()
        mock_ctx.scene.trivesta = mock_settings

        mock_bpy_module.path.abspath.return_value = ""

        op = TRIVESTA_OT_export()
        op.report = MagicMock()
        result = op.execute(mock_ctx)

        assert result == {"CANCELLED"}
        op.report.assert_called_once_with({"ERROR"}, "Export path not set")

    def test_execute_export_failure(self, mock_bpy_module: MagicMock) -> None:
        """Should return CANCELLED when export returns failure result."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        mock_settings = MagicMock()
        mock_settings.export_path = "//exports/"

        mock_ctx = MagicMock()
        mock_ctx.scene.trivesta = mock_settings

        mock_bpy_module.path.abspath.return_value = "/abs/exports/"

        with patch("blender_extension.operators.export.export_world") as mock_export:
            mock_result = MagicMock()
            mock_result.success = False
            mock_result.message = "Missing objects"
            mock_result.files_created = []
            mock_result.errors = ["Object 'Cube' not found"]
            mock_export.return_value = mock_result

            op = TRIVESTA_OT_export()
            result = op.execute(mock_ctx)

            assert result == {"CANCELLED"}

    def test_execute_export_exception(self, mock_bpy_module: MagicMock) -> None:
        """Should return CANCELLED when export raises exception."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        mock_settings = MagicMock()
        mock_settings.export_path = "//exports/"

        mock_ctx = MagicMock()
        mock_ctx.scene.trivesta = mock_settings

        mock_bpy_module.path.abspath.return_value = "/abs/exports/"

        with patch("blender_extension.operators.export.export_world") as mock_export:
            mock_export.side_effect = RuntimeError("Disk full")

            op = TRIVESTA_OT_export()
            op.report = MagicMock()
            result = op.execute(mock_ctx)

            assert result == {"CANCELLED"}
            op.report.assert_called_once_with({"ERROR"}, "Export failed with exception: Disk full")


class TestTrivestaExportOperatorInvoke:
    """Tests for TRIVESTA_OT_export.invoke() method."""

    def test_invoke_small_scene_executes_directly(self, mock_bpy_module: MagicMock) -> None:
        """Should call execute directly when scene has <100 mesh objects."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        # Create 50 mesh objects
        mock_objects = []
        for i in range(50):
            obj = MagicMock()
            obj.type = "MESH"
            obj.visible_get.return_value = True
            mock_objects.append(obj)

        mock_settings = MagicMock()
        mock_settings.export_path = "//exports/"

        mock_ctx = MagicMock()
        mock_ctx.scene.objects = mock_objects
        mock_ctx.scene.trivesta = mock_settings

        mock_bpy_module.path.abspath.return_value = "/abs/exports/"

        mock_event = MagicMock()

        with patch("blender_extension.operators.export.export_world") as mock_export:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.message = "Export complete"
            mock_result.files_created = ["file1.glb"]
            mock_result.errors = []
            mock_export.return_value = mock_result

            op = TRIVESTA_OT_export()
            result = op.invoke(mock_ctx, mock_event)

            assert result == {"FINISHED"}
            mock_ctx.window_manager.invoke_confirm.assert_not_called()

    def test_invoke_large_scene_shows_confirmation(self, mock_bpy_module: MagicMock) -> None:
        """Should show confirmation dialog when scene has >100 mesh objects."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        # Create 150 mesh objects
        mock_objects = []
        for i in range(150):
            obj = MagicMock()
            obj.type = "MESH"
            obj.visible_get.return_value = True
            mock_objects.append(obj)

        mock_ctx = MagicMock()
        mock_ctx.scene.objects = mock_objects
        mock_ctx.window_manager.invoke_confirm.return_value = {"RUNNING_MODAL"}

        mock_event = MagicMock()

        op = TRIVESTA_OT_export()
        result = op.invoke(mock_ctx, mock_event)

        mock_ctx.window_manager.invoke_confirm.assert_called_once_with(op, mock_event)
        assert result == {"RUNNING_MODAL"}

    def test_invoke_counts_only_visible_meshes(self, mock_bpy_module: MagicMock) -> None:
        """Should only count visible mesh objects for confirmation threshold."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        # Create 150 mesh objects, but only 50 visible
        mock_objects = []
        for i in range(150):
            obj = MagicMock()
            obj.type = "MESH"
            obj.visible_get.return_value = i < 50  # Only first 50 visible
            mock_objects.append(obj)

        mock_settings = MagicMock()
        mock_settings.export_path = "//exports/"

        mock_ctx = MagicMock()
        mock_ctx.scene.objects = mock_objects
        mock_ctx.scene.trivesta = mock_settings

        mock_bpy_module.path.abspath.return_value = "/abs/exports/"

        mock_event = MagicMock()

        with patch("blender_extension.operators.export.export_world") as mock_export:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.message = "Export complete"
            mock_result.files_created = ["file1.glb"]
            mock_result.errors = []
            mock_export.return_value = mock_result

            op = TRIVESTA_OT_export()
            result = op.invoke(mock_ctx, mock_event)

            # Should execute directly since only 50 visible meshes
            assert result == {"FINISHED"}
            mock_ctx.window_manager.invoke_confirm.assert_not_called()

    def test_invoke_ignores_non_mesh_objects(self, mock_bpy_module: MagicMock) -> None:
        """Should not count non-mesh objects for confirmation threshold."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        # Create 150 objects, but only 50 are meshes
        mock_objects = []
        for i in range(150):
            obj = MagicMock()
            obj.type = "MESH" if i < 50 else "EMPTY"
            obj.visible_get.return_value = True
            mock_objects.append(obj)

        mock_settings = MagicMock()
        mock_settings.export_path = "//exports/"

        mock_ctx = MagicMock()
        mock_ctx.scene.objects = mock_objects
        mock_ctx.scene.trivesta = mock_settings

        mock_bpy_module.path.abspath.return_value = "/abs/exports/"

        mock_event = MagicMock()

        with patch("blender_extension.operators.export.export_world") as mock_export:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.message = "Export complete"
            mock_result.files_created = ["file1.glb"]
            mock_result.errors = []
            mock_export.return_value = mock_result

            op = TRIVESTA_OT_export()
            result = op.invoke(mock_ctx, mock_event)

            # Should execute directly since only 50 meshes
            assert result == {"FINISHED"}
            mock_ctx.window_manager.invoke_confirm.assert_not_called()


class TestTrivestaExportOperatorReportResult:
    """Tests for TRIVESTA_OT_export._report_result() method."""

    def test_report_result_success_few_files(self, mock_bpy_module: MagicMock) -> None:
        """Should report INFO with file list when <=5 files created."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.message = "Export complete"
        mock_result.files_created = ["file1.glb", "file2.glb", "file3.glb"]
        mock_result.errors = []

        op = TRIVESTA_OT_export()
        op.report = MagicMock()
        op._report_result(mock_result)

        # Should report main message plus each file
        assert op.report.call_count == 4
        op.report.assert_any_call({"INFO"}, "Export complete: Export complete")
        op.report.assert_any_call({"INFO"}, "  Created: file1.glb")
        op.report.assert_any_call({"INFO"}, "  Created: file2.glb")
        op.report.assert_any_call({"INFO"}, "  Created: file3.glb")

    def test_report_result_success_many_files(self, mock_bpy_module: MagicMock) -> None:
        """Should truncate file list when >5 files created."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.message = "Export complete"
        mock_result.files_created = [f"file{i}.glb" for i in range(10)]
        mock_result.errors = []

        op = TRIVESTA_OT_export()
        op.report = MagicMock()
        op._report_result(mock_result)

        # Should report main message + 3 files + "and X more"
        assert op.report.call_count == 5
        op.report.assert_any_call({"INFO"}, "Export complete: Export complete")
        op.report.assert_any_call({"INFO"}, "  Created: file0.glb")
        op.report.assert_any_call({"INFO"}, "  Created: file1.glb")
        op.report.assert_any_call({"INFO"}, "  Created: file2.glb")
        op.report.assert_any_call({"INFO"}, "  ... and 7 more files")

    def test_report_result_failure(self, mock_bpy_module: MagicMock) -> None:
        """Should report ERROR with error list when export fails."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        mock_result = MagicMock()
        mock_result.success = False
        mock_result.message = "Export failed"
        mock_result.files_created = []
        mock_result.errors = ["Error 1", "Error 2"]

        op = TRIVESTA_OT_export()
        op.report = MagicMock()
        op._report_result(mock_result)

        # Should report main error plus each error detail
        assert op.report.call_count == 3
        op.report.assert_any_call({"ERROR"}, "Export failed: Export failed")
        op.report.assert_any_call({"ERROR"}, "  Error 1")
        op.report.assert_any_call({"ERROR"}, "  Error 2")


class TestTrivestaExportOperatorAttributes:
    """Tests for TRIVESTA_OT_export class attributes."""

    def test_bl_idname(self, mock_bpy_module: MagicMock) -> None:
        """Should have correct bl_idname."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        assert TRIVESTA_OT_export.bl_idname == "trivesta.export"

    def test_bl_label(self, mock_bpy_module: MagicMock) -> None:
        """Should have correct bl_label."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        assert TRIVESTA_OT_export.bl_label == "Export Trivesta Level"

    def test_bl_options(self, mock_bpy_module: MagicMock) -> None:
        """Should have REGISTER and UNDO options."""
        from blender_extension.operators.export import TRIVESTA_OT_export

        assert "REGISTER" in TRIVESTA_OT_export.bl_options
        assert "UNDO" in TRIVESTA_OT_export.bl_options
