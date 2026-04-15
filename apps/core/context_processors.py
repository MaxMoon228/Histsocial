from .constants import SITE_BRAND_NAME, SITE_BRAND_TAGLINE


def site_meta(_request):
    return {
        "site_name": SITE_BRAND_NAME,
        "site_tagline": SITE_BRAND_TAGLINE,
    }
