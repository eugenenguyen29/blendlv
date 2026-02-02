"""Tests for Blender scene panel UI.

Tests TRIVESTA_PT_scene_panel draws terrain_export_mode property.
"""

from __future__ import annotations

from unittest.mock import MagicMock


class TestScenePanelTerrainExportMode:
    """Tests for terrain export mode in TRIVESTA_PT_scene_panel."""

    def test_scene_panel_draws_terrain_export_mode(self, mock_bpy_module: MagicMock) -> None:
        """Scene panel should draw terrain_export_mode property."""
        from blender_extension.panels.scene import TRIVESTA_PT_scene_panel

        panel = TRIVESTA_PT_scene_panel()
        mock_layout = MagicMock()
        mock_context = MagicMock()
        mock_context.scene.trivesta = MagicMock()
        mock_context.scene.trivesta.separate_assets = False

        panel.layout = mock_layout
        panel.draw(mock_context)

        # Verify terrain_export_mode was added to layout
        prop_calls = [
            call
            for call in mock_layout.prop.call_args_list
            if len(call[0]) > 1 and call[0][1] == "terrain_export_mode"
        ]
        assert len(prop_calls) > 0, "terrain_export_mode should be drawn in panel"

    def test_scene_panel_terrain_mode_uses_correct_property(
        self, mock_bpy_module: MagicMock
    ) -> None:
        """Terrain export mode should reference settings.terrain_export_mode."""
        from blender_extension.panels.scene import TRIVESTA_PT_scene_panel

        panel = TRIVESTA_PT_scene_panel()
        mock_layout = MagicMock()
        mock_context = MagicMock()
        mock_settings = MagicMock()
        mock_settings.separate_assets = False
        mock_context.scene.trivesta = mock_settings

        panel.layout = mock_layout
        panel.draw(mock_context)

        # Find the terrain_export_mode prop call
        prop_calls = [
            call
            for call in mock_layout.prop.call_args_list
            if len(call[0]) > 1 and call[0][1] == "terrain_export_mode"
        ]
        assert len(prop_calls) == 1

        # Verify it uses the correct settings object
        prop_call = prop_calls[0]
        assert prop_call[0][0] is mock_settings, "terrain_export_mode should use settings object"
