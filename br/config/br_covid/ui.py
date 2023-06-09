# # -*- coding: utf-8 -*-
from config.br_covid.datatypes import HIERARCHICAL_DIMENSIONS

# pylint: disable=C0301
############################################################################
# General frontend UI configuration.

# Shows in top left.
FULL_PLATFORM_NAME = 'IVIS'

# Classname for country flag.
FLAG_CLASS = 'flag-br'

# Default language
DEFAULT_LOCALE = 'pt'

# Translations to offer.
ENABLE_LOCALES = ['en', 'pt']

# Favicon browser icon.
FAVICON_PATH = '/images/favicon.png'

# Save to home icon.
HOME_ICON_PATH = '/images/favicon.png'

# If set, LOGO_PATH overrides the flag shown at the top of the navbar.
LOGO_PATH = None

############################################################################
# Query Form UI

# Whether to show Ethiopian date selector.
ENABLE_ET_DATE_SELECTION = False

############################################################################
# Timeseries UI

# Whether to show Ethiopian dates instead of Gregorian dates on timeseries.
TIMESERIES_USE_ET_DATES = False

# The default time granularity the timeseries should use.
TIMESERIES_DEFAULT_GRANULARITY = 'month'

############################################################################
# Map UI

# Two letter ISO country code
COUNTRY_CODE = 'br'

# Center of map view.
MAP_DEFAULT_LATLNG = [-14.2350, -51.9253]

# Default zoom level.
MAP_DEFAULT_ZOOM = 4

# GeoJson Tile Overlay
MAP_GEOJSON_LOCATION = (
    'https://dvvivclrsb6tx.cloudfront.net/br_covid/geojson/brazil-20220328.geojson'
)

# Static geo data locations.
GEO_DATA_URL = ''

# Dimension and the children dimensions for geo data.
GEO_DATA_DIMENSIONS = ''

# List of keys to be displayed.
GEO_DATA_DISPLAY = []

# The key to use to display a value in the map labels (for entity markers only).
# This will change if we decide to show multiple values per entity.
GEO_DATA_LABEL_KEY = ''

# A model that represents settings associated with our GIS tool. This stores
# information such as dataset URLs, names of datasets, keys to filter on, etc.
GIS_APP_SETTINGS = None

# List of geo dimensions that can be shown on the dql map viz
DQL_MAP_DIMENSIONS = HIERARCHICAL_DIMENSIONS

# Mapbox access token.
MAPBOX_ACCESS_TOKEN = ''

############################################################################
# Misc
# New user google form
FEED_BACK_REGISTRATION_LINK = None

# User manual link in nav menu.
USER_MANUAL_URL = None

# Give users a link/tab for data quality
ENABLE_DATA_QUALITY_LAB = False

# Session timeout in seconds
SESSION_TIMEOUT = 1800

# Up to nine custom colors for the deployment
CUSTOM_COLORS = []
