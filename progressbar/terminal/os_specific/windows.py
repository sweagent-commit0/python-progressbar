"""
Windows specific code for the terminal.

Note that the naming convention here is non-pythonic because we are
matching the Windows API naming.
"""
from __future__ import annotations
import ctypes
import enum
from ctypes.wintypes import BOOL as _BOOL, CHAR as _CHAR, DWORD as _DWORD, HANDLE as _HANDLE, SHORT as _SHORT, UINT as _UINT, WCHAR as _WCHAR, WORD as _WORD
_kernel32 = ctypes.windll.Kernel32
_STD_INPUT_HANDLE = _DWORD(-10)
_STD_OUTPUT_HANDLE = _DWORD(-11)

class WindowsConsoleModeFlags(enum.IntFlag):
    ENABLE_ECHO_INPUT = 4
    ENABLE_EXTENDED_FLAGS = 128
    ENABLE_INSERT_MODE = 32
    ENABLE_LINE_INPUT = 2
    ENABLE_MOUSE_INPUT = 16
    ENABLE_PROCESSED_INPUT = 1
    ENABLE_QUICK_EDIT_MODE = 64
    ENABLE_WINDOW_INPUT = 8
    ENABLE_VIRTUAL_TERMINAL_INPUT = 512
    ENABLE_PROCESSED_OUTPUT = 1
    ENABLE_WRAP_AT_EOL_OUTPUT = 2
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 4
    DISABLE_NEWLINE_AUTO_RETURN = 8
    ENABLE_LVB_GRID_WORLDWIDE = 16

    def __str__(self):
        return f'{self.name} (0x{self.value:04X})'
_GetConsoleMode = _kernel32.GetConsoleMode
_GetConsoleMode.restype = _BOOL
_SetConsoleMode = _kernel32.SetConsoleMode
_SetConsoleMode.restype = _BOOL
_GetStdHandle = _kernel32.GetStdHandle
_GetStdHandle.restype = _HANDLE
_ReadConsoleInput = _kernel32.ReadConsoleInputA
_ReadConsoleInput.restype = _BOOL
_h_console_input = _GetStdHandle(_STD_INPUT_HANDLE)
_input_mode = _DWORD()
_GetConsoleMode(_HANDLE(_h_console_input), ctypes.byref(_input_mode))
_h_console_output = _GetStdHandle(_STD_OUTPUT_HANDLE)
_output_mode = _DWORD()
_GetConsoleMode(_HANDLE(_h_console_output), ctypes.byref(_output_mode))

class _COORD(ctypes.Structure):
    _fields_ = (('X', _SHORT), ('Y', _SHORT))

class _FOCUS_EVENT_RECORD(ctypes.Structure):
    _fields_ = (('bSetFocus', _BOOL),)

class _KEY_EVENT_RECORD(ctypes.Structure):

    class _uchar(ctypes.Union):
        _fields_ = (('UnicodeChar', _WCHAR), ('AsciiChar', _CHAR))
    _fields_ = (('bKeyDown', _BOOL), ('wRepeatCount', _WORD), ('wVirtualKeyCode', _WORD), ('wVirtualScanCode', _WORD), ('uChar', _uchar), ('dwControlKeyState', _DWORD))

class _MENU_EVENT_RECORD(ctypes.Structure):
    _fields_ = (('dwCommandId', _UINT),)

class _MOUSE_EVENT_RECORD(ctypes.Structure):
    _fields_ = (('dwMousePosition', _COORD), ('dwButtonState', _DWORD), ('dwControlKeyState', _DWORD), ('dwEventFlags', _DWORD))

class _WINDOW_BUFFER_SIZE_RECORD(ctypes.Structure):
    _fields_ = (('dwSize', _COORD),)

class _INPUT_RECORD(ctypes.Structure):

    class _Event(ctypes.Union):
        _fields_ = (('KeyEvent', _KEY_EVENT_RECORD), ('MouseEvent', _MOUSE_EVENT_RECORD), ('WindowBufferSizeEvent', _WINDOW_BUFFER_SIZE_RECORD), ('MenuEvent', _MENU_EVENT_RECORD), ('FocusEvent', _FOCUS_EVENT_RECORD))
    _fields_ = (('EventType', _WORD), ('Event', _Event))