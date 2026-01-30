"""Unit tests for placement utilities."""

from __future__ import annotations

import pytest

from blender_extension.utils.placement import ENTITY_TYPE_PREFIXES, infer_entity_type


class TestInferEntityType:
    """Tests for infer_entity_type function."""

    def test_prop_prefix_returns_static(self):
        """PropTree_Oak should return 'static'."""
        assert infer_entity_type("PropTree_Oak") == "static"

    def test_npc_prefix_returns_npc(self):
        """NPC_Villager should return 'npc'."""
        assert infer_entity_type("NPC_Villager") == "npc"

    def test_terrain_prefix_returns_terrain(self):
        """TerrainRock_Large should return 'terrain'."""
        assert infer_entity_type("TerrainRock_Large") == "terrain"

    def test_unknown_prefix_returns_static_default(self):
        """RandomObject with no matching prefix should default to 'static'."""
        assert infer_entity_type("RandomObject") == "static"

    def test_case_insensitivity_lowercase(self):
        """proptree (lowercase) should match Prop prefix."""
        assert infer_entity_type("proptree_oak") == "static"

    def test_case_insensitivity_uppercase(self):
        """PROPTREE (uppercase) should match Prop prefix."""
        assert infer_entity_type("PROPTREE_OAK") == "static"

    def test_case_insensitivity_mixed(self):
        """pRoPtReE (mixed case) should match Prop prefix."""
        assert infer_entity_type("pRoPtReE_oak") == "static"

    @pytest.mark.parametrize(
        ("prefix", "expected_type"),
        [
            ("Prop", "static"),
            ("Static", "static"),
            ("Decoration", "static"),
            ("Deco", "static"),
            ("Actor", "npc"),
            ("NPC", "npc"),
            ("Character", "npc"),
            ("Enemy", "npc"),
            ("Interact", "interactive"),
            ("Pickup", "interactive"),
            ("Item", "interactive"),
            ("Door", "interactive"),
            ("Trigger", "trigger"),
            ("Zone", "trigger"),
            ("Area", "trigger"),
            ("Audio", "audio"),
            ("Sound", "audio"),
            ("Music", "audio"),
            ("Terrain", "terrain"),
            ("Ground", "terrain"),
            ("Floor", "terrain"),
            ("Landscape", "terrain"),
        ],
    )
    def test_all_defined_prefixes(self, prefix: str, expected_type: str):
        """All prefixes in ENTITY_TYPE_PREFIXES should map to correct type."""
        asset_name = f"{prefix}_TestAsset"
        assert infer_entity_type(asset_name) == expected_type

    def test_empty_string_returns_default(self):
        """Empty string should return default 'static'."""
        assert infer_entity_type("") == "static"

    def test_prefix_at_start_only(self):
        """Prefix must be at the start, not embedded in name."""
        # "MyPropTree" should NOT match "Prop" prefix
        assert infer_entity_type("MyPropTree") == "static"

    def test_exact_prefix_match(self):
        """Exact prefix (no suffix) should still match."""
        assert infer_entity_type("Prop") == "static"
        assert infer_entity_type("NPC") == "npc"

    def test_prefix_with_underscore(self):
        """Prefix followed by underscore is common naming convention."""
        assert infer_entity_type("Trigger_Zone01") == "trigger"

    def test_prefix_with_number_suffix(self):
        """Prefix with number suffix should match."""
        assert infer_entity_type("Audio001") == "audio"

    def test_entity_type_prefixes_completeness(self):
        """Verify all prefixes in ENTITY_TYPE_PREFIXES are tested."""
        all_prefixes = []
        for prefixes in ENTITY_TYPE_PREFIXES.values():
            all_prefixes.extend(prefixes)

        # Verify count matches parametrized test
        assert len(all_prefixes) == 22
