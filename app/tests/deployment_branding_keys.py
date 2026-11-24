"""The ONE place where the tests of the deployment branding name the banner keys.

D-0411 renamed the banner keys of the deployment: `title` -> `ui_label`, `subtitle` -> `description` (built in the names pass).
The VALUES the tests expect did not change; only the two names below did.
"""
BANNER_TITLE_KEY = "ui_label"
BANNER_LINE_KEY = "description"
BANNER_LOGO_KEY = "logo_url"


def banner_title(banner):
    """The banner title as a deployment file or the bootloader gives it ('' when absent)."""
    return (banner or {}).get(BANNER_TITLE_KEY) or ""


def banner_line(banner):
    """The banner line under the title ('' when absent)."""
    return (banner or {}).get(BANNER_LINE_KEY) or ""


def banner_logo(banner):
    """The logo path of the banner ('' when absent)."""
    return (banner or {}).get(BANNER_LOGO_KEY) or ""
