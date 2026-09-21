from __future__ import annotations

from pathlib import Path
import sys

from pm_decision.constants import FOLDER_PICKER_TITLE


def pick_folder(initial_directory: Path, title: str = FOLDER_PICKER_TITLE) -> Path | None:
    if sys.platform != "win32":
        raise RuntimeError("O seletor de pasta nativo está disponível apenas no Windows.")
    selected = _pick_folder_windows(initial_directory, title)
    if not selected:
        return None
    path = Path(selected)
    if not path.is_dir():
        return None
    return path.resolve()


def _pick_folder_windows(initial_directory: Path, title: str) -> str | None:
    import ctypes
    from ctypes import POINTER, byref, c_void_p, HRESULT, windll
    from ctypes.wintypes import DWORD, HWND, LPCWSTR, LPWSTR

    ole32 = windll.ole32
    shell32 = windll.shell32

    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", ctypes.c_uint32),
            ("Data2", ctypes.c_uint16),
            ("Data3", ctypes.c_uint16),
            ("Data4", ctypes.c_ubyte * 8),
        ]

    def guid_from_string(value: str) -> GUID:
        guid = GUID()
        ole32.CLSIDFromString.argtypes = [LPCWSTR, POINTER(GUID)]
        ole32.CLSIDFromString.restype = HRESULT
        result = ole32.CLSIDFromString(value, byref(guid))
        if result != 0:
            raise OSError(f"CLSIDFromString failed: {result}")
        return guid

    CLSID_FileOpenDialog = guid_from_string("{DC1C5A9C-E88A-4dde-A5A1-60F82A20AEF7}")
    IID_IFileOpenDialog = guid_from_string("{D57C7288-D4AD-4768-BE02-9D969532D960}")
    IID_IShellItem = guid_from_string("{43826D1E-E718-42EE-BC55-A1E261C37BFE}")

    CLSCTX_INPROC_SERVER = 1
    FOS_PICKFOLDERS = 0x20
    FOS_FORCEFILESYSTEM = 0x40
    SIGDN_FILESYSPATH = 0x80058000
    S_OK = 0
    HRESULT_CANCELLED = 0x800704C7

    ole32.CoInitialize(None)
    dialog_ptr = c_void_p()
    ole32.CoCreateInstance.argtypes = [
        POINTER(GUID),
        c_void_p,
        DWORD,
        POINTER(GUID),
        POINTER(c_void_p),
    ]
    ole32.CoCreateInstance.restype = HRESULT
    created = ole32.CoCreateInstance(
        byref(CLSID_FileOpenDialog),
        None,
        CLSCTX_INPROC_SERVER,
        byref(IID_IFileOpenDialog),
        byref(dialog_ptr),
    )
    if created != S_OK or not dialog_ptr.value:
        raise OSError("Não foi possível abrir o diálogo nativo de pasta.")

    vtable = ctypes.cast(dialog_ptr, POINTER(POINTER(c_void_p))).contents

    def com_method(index: int, restype, *argtypes):
        prototype = ctypes.WINFUNCTYPE(restype, c_void_p, *argtypes)
        return prototype(vtable[index])

    set_options = com_method(9, HRESULT, DWORD)
    set_title = com_method(17, HRESULT, LPCWSTR)
    set_folder = com_method(12, HRESULT, c_void_p)
    show_dialog = com_method(3, HRESULT, HWND)
    get_result = com_method(20, HRESULT, POINTER(c_void_p))
    release = com_method(2, ctypes.c_ulong)

    set_options(dialog_ptr, FOS_PICKFOLDERS | FOS_FORCEFILESYSTEM)
    set_title(dialog_ptr, title)

    if initial_directory.exists():
        shell32.SHCreateItemFromParsingName.argtypes = [
            LPCWSTR,
            c_void_p,
            POINTER(GUID),
            POINTER(c_void_p),
        ]
        shell32.SHCreateItemFromParsingName.restype = HRESULT
        folder_item = c_void_p()
        item_created = shell32.SHCreateItemFromParsingName(
            str(initial_directory.resolve()),
            None,
            byref(IID_IShellItem),
            byref(folder_item),
        )
        if item_created == S_OK and folder_item.value:
            set_folder(dialog_ptr, folder_item)

    show_result = show_dialog(dialog_ptr, None)
    if show_result == HRESULT_CANCELLED or show_result != S_OK:
        release(dialog_ptr)
        return None

    result_item = c_void_p()
    got_result = get_result(dialog_ptr, byref(result_item))
    if got_result != S_OK or not result_item.value:
        release(dialog_ptr)
        return None

    item_vtable = ctypes.cast(result_item, POINTER(POINTER(c_void_p))).contents
    get_display_name = ctypes.WINFUNCTYPE(HRESULT, c_void_p, ctypes.c_int, POINTER(LPWSTR))(
        item_vtable[5]
    )
    release_item = ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)(item_vtable[2])
    path_ptr = LPWSTR()
    named = get_display_name(result_item, SIGDN_FILESYSPATH, byref(path_ptr))
    selected_path = path_ptr.value if named == S_OK else None
    if path_ptr:
        windll.ole32.CoTaskMemFree(path_ptr)
    release_item(result_item)
    release(dialog_ptr)
    return selected_path


def main() -> int:
    initial = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home()
    selected = pick_folder(initial)
    if selected is None:
        return 2
    sys.stdout.write(str(selected))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
