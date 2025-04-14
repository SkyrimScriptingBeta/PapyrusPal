import json
import sys
import io
from typing import Dict, List, Optional, Any

# Force stdout to UTF-8 so emojis and symbols don't crash Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

LICENSE_FILE: str = "skyrim_papyrus_repos.json"


def classify_license(license_info: Optional[Dict[str, Any]]) -> str:
    if license_info is None:
        return "NONE"

    spdx_id: Optional[str] = license_info.get("spdx_id")
    if spdx_id is None or spdx_id.upper() == "NOASSERTION":
        return "CUSTOM"

    if spdx_id.upper() in {
        "MIT",
        "APACHE-2.0",
        "WTFPL",
        "BSD-2-CLAUSE",
        "BSD-3-CLAUSE",
        "0BSD",
    }:
        return "PERMISSIVE"

    if spdx_id.upper() in {"GPL-3.0", "LGPL-3.0", "EPL-2.0"}:
        return "COPYLEFT"

    return license_info.get("name", "UNKNOWN")


def main() -> None:
    with open(LICENSE_FILE, "r", encoding="utf-8") as f:
        repos: List[Dict[str, Any]] = json.load(f)

    count_of_permissive = 0
    for repo in repos:
        url: str = repo.get("html_url", "")
        description: str = (repo.get("description") or "").strip()
        license_info: Optional[Dict[str, Any]] = repo.get("license")

        license_type: str = classify_license(license_info)

        # Override a few of them...
        overrides_by_url: Dict[str, str] = {
            "https://github.com/nbits-ssl/EcchinaArmorBreak": "PERMISSIVE",  # MIT
            "https://github.com/nbits-ssl/ItsNotYourArmor": "PERMISSIVE",  # MIT
            "https://github.com/nbits-ssl/SexLabYACR4N": "PERMISSIVE",  # MIT
            "https://github.com/phalanx/Children-of-Lilith": "PERMISSIVE",  # MIT
            "https://github.com/slacksystem/Immersive-Pickup-Only": "NON-COMMERCIAL",
            "https://github.com/alexstrout/SkyrimSE": "NON-COMMERCIAL",
            "https://github.com/CPULL/Skyrim-Pole-Dances-Framework": "NON-COMMERCIAL",
            "https://github.com/alexstrout/SkyrimClassic": "NON-COMMERCIAL",
            "https://github.com/ceejbot/firestarter": "COPYLEFT",
            "https://github.com/nbits-ssl/SexLabYACR": "PERMISSIVE",
        }

        # override the license_type of repo is in the overrides_by_url
        if url in overrides_by_url:
            license_type = overrides_by_url[url]

        if license_type not in {"NONE", "GPL 3.0", "NON-COMMERCIAL"}:

            if license_type == "PERMISSIVE":
                count_of_permissive += 1

            if not license_type in {"COPYLEFT", "PERMISSIVE", "NON-COMMERCIAL"}:
                print("=" * 80)
                print(f"URL        : {url}")
                print(f"Description: {description}")
                print(f"License    : {license_type}")

                # if license_type == "CUSTOM":
                print("Full license object:")
                print(json.dumps(license_info, indent=2, ensure_ascii=False))

    print("=" * 80)
    print(f"Total permissive licenses: {count_of_permissive}")


if __name__ == "__main__":
    main()
