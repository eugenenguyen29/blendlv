"""Base class for Trivesta Level E2E tests.

Provides:
- Extension installation/cleanup via test repository
- Scene reset between tests for isolation
- Common test utilities
"""

import unittest
from pathlib import Path


class TrivestaTestCase(unittest.TestCase):
    """Base class for Trivesta Level E2E tests.

    Subclass this to get automatic extension installation/cleanup
    and scene reset between tests.

    Example:
        class TestMyFeature(TrivestaTestCase):
            def test_something(self):
                import bpy
                # Extension is already installed
                self.assertTrue(hasattr(bpy.ops.trivesta, 'export'))
    """

    module_path: str = ""

    @classmethod
    def setUpClass(cls) -> None:
        """Install Trivesta Level extension via test repository."""
        import bpy

        # Get project root (tests/e2e -> tests -> project root)
        repo = str(Path(__file__).parent.parent.parent)

        # Reset to factory settings for clean state
        bpy.ops.wm.read_factory_settings(use_factory_startup_app_template_only=True)

        # Create test repository pointing to project root
        repo_module = "test_repo"
        bpy.context.preferences.extensions.repos.new(
            name="Test Repo",
            module=repo_module,
            custom_directory=repo,
            source="USER",
        )

        # Enable the extension
        cls.module_path = "bl_ext." + repo_module + ".blender_extension"
        bpy.ops.preferences.addon_enable(module=cls.module_path)

    def setUp(self) -> None:
        """Reset scene between tests for isolation."""
        import bpy

        bpy.ops.wm.read_homefile()

    @classmethod
    def tearDownClass(cls) -> None:
        """Disable extension after tests."""
        import bpy

        try:
            bpy.ops.preferences.addon_disable(module=cls.module_path)
        except Exception:
            pass  # Extension may already be disabled
