"""Dialog management operators for NPC dialog lines.

Provides operators for adding, removing, and reordering dialog lines
in the TrivestaObjectSettings dialog_lines CollectionProperty.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.props import EnumProperty
from bpy.types import Operator, UIList

if TYPE_CHECKING:
    from bpy.types import Context, Event


class TRIVESTA_OT_add_dialog_line(Operator):
    """Add a new dialog line to the NPC."""

    bl_idname = "trivesta.add_dialog_line"
    bl_label = "Add Dialog Line"
    bl_description = "Add a new dialog line entry"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[str]:
        """Add a new dialog line with default values."""
        obj = context.object
        if not obj or not hasattr(obj, "trivesta"):
            return {"CANCELLED"}

        settings = obj.trivesta
        item = settings.dialog_lines.add()
        item.speaker = ""
        item.text = ""
        settings.dialog_line_index = len(settings.dialog_lines) - 1

        return {"FINISHED"}


class TRIVESTA_OT_remove_dialog_line(Operator):
    """Remove the selected dialog line."""

    bl_idname = "trivesta.remove_dialog_line"
    bl_label = "Remove Dialog Line"
    bl_description = "Remove the selected dialog line entry"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Only enable when dialog lines exist."""
        obj = context.object
        if not obj or not hasattr(obj, "trivesta"):
            return False
        return len(obj.trivesta.dialog_lines) > 0

    def execute(self, context: Context) -> set[str]:
        """Remove the selected dialog line and adjust index."""
        obj = context.object
        settings = obj.trivesta
        index = settings.dialog_line_index

        settings.dialog_lines.remove(index)
        # Clamp index to valid range
        settings.dialog_line_index = min(max(0, index), len(settings.dialog_lines) - 1)

        return {"FINISHED"}


class TRIVESTA_OT_move_dialog_line(Operator):
    """Move dialog line up or down in the list."""

    bl_idname = "trivesta.move_dialog_line"
    bl_label = "Move Dialog Line"
    bl_description = "Reorder dialog line position"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(
        items=[
            ("UP", "Up", "Move line up"),
            ("DOWN", "Down", "Move line down"),
        ],
        default="UP",
        options={"HIDDEN", "SKIP_SAVE"},
    )

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Only enable when dialog lines exist."""
        obj = context.object
        if not obj or not hasattr(obj, "trivesta"):
            return False
        return len(obj.trivesta.dialog_lines) > 0

    def execute(self, context: Context) -> set[str]:
        """Move the selected dialog line up or down."""
        obj = context.object
        settings = obj.trivesta
        index = settings.dialog_line_index
        count = len(settings.dialog_lines)

        new_index = index
        if self.direction == "UP":
            new_index = max(0, index - 1)
        elif self.direction == "DOWN":
            new_index = min(count - 1, index + 1)

        if new_index != index:
            settings.dialog_lines.move(index, new_index)
            settings.dialog_line_index = new_index

        return {"FINISHED"}


class TRIVESTA_OT_edit_dialog(Operator):
    """Edit NPC dialog in popup modal."""

    bl_idname = "trivesta.edit_dialog"
    bl_label = "Edit Dialog"
    bl_description = "Open dialog editor in popup window"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Only enable when object exists with trivesta attribute."""
        return context.object is not None and hasattr(context.object, "trivesta")

    def invoke(self, context: Context, event: Event) -> set[str]:
        """Open popup dialog."""
        return context.window_manager.invoke_popup(self, width=500)

    def draw(self, context: Context) -> None:
        """Draw popup UI with dialog editor."""
        layout = self.layout
        obj = context.object
        settings = obj.trivesta

        # Dialog list with controls
        box = layout.box()
        box.label(text="Dialog Lines", icon="TEXT")

        row = box.row()
        row.template_list(
            "TRIVESTA_UL_dialog_list",
            "",
            settings,
            "dialog_lines",
            settings,
            "dialog_line_index",
            rows=6,
        )

        col = row.column(align=True)
        col.operator("trivesta.add_dialog_line", icon="ADD", text="")
        col.operator("trivesta.remove_dialog_line", icon="REMOVE", text="")
        col.separator()
        col.operator("trivesta.move_dialog_line", icon="TRIA_UP", text="").direction = (
            "UP"
        )
        col.operator(
            "trivesta.move_dialog_line", icon="TRIA_DOWN", text=""
        ).direction = "DOWN"

        # Edit selected line
        if len(settings.dialog_lines) > 0:
            layout.separator()
            box = layout.box()
            box.label(text="Edit Selected Line", icon="GREASEPENCIL")

            index = settings.dialog_line_index
            if 0 <= index < len(settings.dialog_lines):
                line = settings.dialog_lines[index]
                box.prop(line, "speaker", text="Speaker")
                box.prop(line, "text", text="Text")

    def execute(self, context: Context) -> set[str]:
        """Called when popup closes."""
        return {"FINISHED"}


class TRIVESTA_UL_dialog_list(UIList):
    """UI List for displaying NPC dialog lines."""

    bl_idname = "TRIVESTA_UL_dialog_list"

    def draw_item(
        self,
        context: Context,
        layout,
        data,
        item,
        icon: int,
        active_data,
        active_property: str,
        index: int = 0,
        flt_flag: int = 0,
    ) -> None:
        """Draw a single dialog line item.

        Args:
            context: Blender context.
            layout: UILayout to draw in.
            data: Data containing the collection.
            item: Dialog line item to draw.
            icon: Icon to display.
            active_data: Data containing active index.
            active_property: Name of active index property.
            index: Item index in collection.
            flt_flag: Filter flag.
        """
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            # Speaker with fallback
            speaker_text = item.speaker if item.speaker else "(No speaker)"
            row.label(text=speaker_text, icon="USER")
            # Text with truncation and fallback
            if item.text:
                text_display = item.text[:40] + "..." if len(item.text) > 40 else item.text
            else:
                text_display = "(Empty)"
            row.label(text=text_display)
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon="TEXT")


__all__ = [
    "TRIVESTA_OT_add_dialog_line",
    "TRIVESTA_OT_remove_dialog_line",
    "TRIVESTA_OT_move_dialog_line",
    "TRIVESTA_OT_edit_dialog",
    "TRIVESTA_UL_dialog_list",
]
