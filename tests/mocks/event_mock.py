"""Blender event mock factory for testing.

Provides configurable event mocks that simulate Blender's Event
object with mouse position, event type, and value.
"""

from __future__ import annotations

from unittest.mock import MagicMock


def create_event_mock(
    event_type: str = "MOUSEMOVE",
    value: str = "PRESS",
    mouse_x: int = 960,
    mouse_y: int = 540,
    mouse_prev_x: int | None = None,
    mouse_prev_y: int | None = None,
    mouse_region_x: int | None = None,
    mouse_region_y: int | None = None,
    shift: bool = False,
    ctrl: bool = False,
    alt: bool = False,
    oskey: bool = False,
) -> MagicMock:
    """Create a Blender event mock.

    Args:
        event_type: Event type (MOUSEMOVE, LEFTMOUSE, RIGHTMOUSE, ESC, etc.)
        value: Event value (PRESS, RELEASE, CLICK, NOTHING, etc.)
        mouse_x: Absolute mouse x position (screen coordinates)
        mouse_y: Absolute mouse y position (screen coordinates)
        mouse_prev_x: Previous mouse x (defaults to mouse_x)
        mouse_prev_y: Previous mouse y (defaults to mouse_y)
        mouse_region_x: Mouse x relative to region (auto-calculated if None)
        mouse_region_y: Mouse y relative to region (auto-calculated if None)
        shift: Shift key held
        ctrl: Control key held
        alt: Alt key held
        oskey: OS key held (Cmd on Mac, Win on Windows)

    Returns:
        Configured MagicMock simulating bpy.types.Event
    """
    event = MagicMock()

    # Event type and value
    event.type = event_type
    event.value = value

    # Mouse position (absolute screen coordinates)
    event.mouse_x = mouse_x
    event.mouse_y = mouse_y

    # Previous mouse position
    event.mouse_prev_x = mouse_prev_x if mouse_prev_x is not None else mouse_x
    event.mouse_prev_y = mouse_prev_y if mouse_prev_y is not None else mouse_y

    # Region-relative coordinates (often used for 2D to 3D projection)
    # If not provided, use same as absolute (assumes region at 0,0)
    event.mouse_region_x = mouse_region_x if mouse_region_x is not None else mouse_x
    event.mouse_region_y = mouse_region_y if mouse_region_y is not None else mouse_y

    # Modifier keys
    event.shift = shift
    event.ctrl = ctrl
    event.alt = alt
    event.oskey = oskey

    # Tablet pressure (1.0 = full pressure, or mouse click)
    event.pressure = 1.0

    # Is tablet pen event
    event.is_tablet = False

    # Unicode character for text input events
    event.unicode = ""
    event.ascii = ""

    return event


def create_mouse_move_event(
    x: int = 960,
    y: int = 540,
    prev_x: int | None = None,
    prev_y: int | None = None,
) -> MagicMock:
    """Create a MOUSEMOVE event.

    Args:
        x: Current mouse x
        y: Current mouse y
        prev_x: Previous mouse x (defaults to x)
        prev_y: Previous mouse y (defaults to y)

    Returns:
        Event mock configured as MOUSEMOVE
    """
    return create_event_mock(
        event_type="MOUSEMOVE",
        value="NOTHING",
        mouse_x=x,
        mouse_y=y,
        mouse_prev_x=prev_x,
        mouse_prev_y=prev_y,
    )


def create_left_click_event(
    x: int = 960,
    y: int = 540,
    value: str = "PRESS",
) -> MagicMock:
    """Create a LEFTMOUSE event.

    Args:
        x: Mouse x position
        y: Mouse y position
        value: PRESS or RELEASE

    Returns:
        Event mock configured as left mouse button
    """
    return create_event_mock(
        event_type="LEFTMOUSE",
        value=value,
        mouse_x=x,
        mouse_y=y,
    )


def create_right_click_event(
    x: int = 960,
    y: int = 540,
    value: str = "PRESS",
) -> MagicMock:
    """Create a RIGHTMOUSE event.

    Args:
        x: Mouse x position
        y: Mouse y position
        value: PRESS or RELEASE

    Returns:
        Event mock configured as right mouse button
    """
    return create_event_mock(
        event_type="RIGHTMOUSE",
        value=value,
        mouse_x=x,
        mouse_y=y,
    )


def create_key_event(
    key: str = "A",
    value: str = "PRESS",
    shift: bool = False,
    ctrl: bool = False,
    alt: bool = False,
) -> MagicMock:
    """Create a keyboard event.

    Args:
        key: Key identifier (A-Z, ESC, RET, SPACE, etc.)
        value: PRESS or RELEASE
        shift: Shift modifier
        ctrl: Control modifier
        alt: Alt modifier

    Returns:
        Event mock configured as keyboard event
    """
    return create_event_mock(
        event_type=key,
        value=value,
        shift=shift,
        ctrl=ctrl,
        alt=alt,
    )


def create_escape_event() -> MagicMock:
    """Create an ESC key press event.

    Returns:
        Event mock configured as ESC press
    """
    return create_key_event(key="ESC", value="PRESS")
