"""The ONE place where the tests of the deployment branding name the banner keys.

D-0411 (owner decision, not built yet) renames the banner keys `title` -> `ui_label` and `subtitle` -> `description`.
When that is built, only the two names below change; the VALUES the tests expect stay the same.
"""
BANNER_TITLE_KEY = "title"
BANNER_LINE_KEY = "subtitle"
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
