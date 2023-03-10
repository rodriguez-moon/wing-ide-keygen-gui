from __future__ import annotations

import hashlib
import re
import tkinter.messagebox
from secrets import SystemRandom
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .gui import Application

BASE30 = "123456789ABCDEFGHJKLMNPQRTVWXY"


class WingKeygen:
    version_magics = {
        "9.0.0+": (7, 42, 17, 123),
        "8.X.X": (245, 45, 95, 179),
        "7.X.X": (27, 93, 13, 221),
        "6.X.X": (9, 47, 161, 23),
        "5.X.X": (87, 23, 123, 7),
    }
    license_types = {
        "Commercial": "CN",
        "Non-Commercial": "EN",
        "Educational": "NN",
        "Trial/Evaluation": "tN",
    }
    # RW for Windows, RL for Linux, RM for MacOS
    request_regex = r"^R[LMW][A-HJ-NP-RTV-Y1-9]{3}(-[A-HJ-NP-RTV-Y1-9]{5}){3}$"
    license_regex = r"^[TNECYH6][NL][A-HJ-NP-RTV-Y1-9]{3}(-[A-HJ-NP-RTV-Y1-9]{5}){3}$"

    @staticmethod
    def add_hyphens(n: int, char: str = "-") -> Callable[[Any], Any]:
        def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
            def wrapper(*args: Any, **kwargs: Any) -> str:
                res = func(*args, **kwargs)
                return char.join(res[i : i + n] for i in range(0, len(res), n))

            return wrapper

        return decorator

    @staticmethod
    def int_to_b30(div: int) -> str:
        res = str()
        while div:
            div, rem = divmod(div, 30)
            res += BASE30[rem]
        return res[::-1].rjust(17, "1")

    @staticmethod
    def loop(ecx: int, chars: str) -> int:
        part = int()
        for c in chars:
            part *= ecx
            part += ord(c)
        return part & 0xFFFFF

    @add_hyphens(5)
    def create_license_id(self, ltype: str) -> str:
        cryptosecure = SystemRandom()
        license = (
            self.license_types[ltype]
            + cryptosecure.choice(re.subn("[LMW]", "", BASE30)[0])
            + "".join(cryptosecure.choices(BASE30, k=17))
        )
        return license

    @add_hyphens(5)
    def get_license_hash(self, license_id: str, request_id: str) -> str:
        hasher = hashlib.sha1()
        hasher.update(request_id.encode("ascii"))
        hasher.update(license_id.encode("ascii"))
        hash_int = int(hasher.hexdigest().upper()[::2], 16)
        return request_id[:3] + self.int_to_b30(hash_int)

    @add_hyphens(5)
    def get_activation_code(
        self,
        license_hash: str,
        version_magic: tuple[int, int, int, int],
    ) -> str:
        return "AXX" + self.int_to_b30(
            sum(
                self.loop(j, license_hash) << i * 20
                for i, j in enumerate(version_magic)
            )
        ).ljust(17, "1")

    def generate_license(self, app: Application) -> None:
        version = app.version_info.get().strip()
        version_magic = self.version_magics.get(version)
        if version_magic is None:
            tkinter.messagebox.showerror("Error", "Invalid Wing IDE Pro Version.")
            return

        request_code = app.request_code.get().upper().strip()
        license_id = app.license_id.get().upper().strip()

        if re.match(self.license_regex, license_id) is None:
            tkinter.messagebox.showerror("Error", "Invalid license ID.")
            return

        if re.match(self.request_regex, request_code) is None:
            tkinter.messagebox.showerror("Error", "Invalid request code.")
            return

        license_hash = self.get_license_hash(license_id, request_code)
        activation_code = self.get_activation_code(license_hash, version_magic)

        print(f"\n[*] Wing IDE Version: {version}")
        print(f"[*] License ID      : {license_id}")
        print(f"[*] Request Code    : {request_code}")
        print(f"[*] Activation Code : {activation_code}")
        app.activation_code.set(activation_code)


if __name__ == "__main__":
    print("[x] Please run 'main.py'!")
    raise SystemExit(1)
