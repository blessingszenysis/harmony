from config.br_covid.aggregation import DIMENSIONS
from config.br_covid.datatypes import BaseRowType

# Dimensions that should not be filterable for users
EXCLUDE_FILTER_DIMENSIONS = set()

# List of dimensions that will display in the filter dropdown and be filterable.
# Include the source dimension and any others in AQT, exclude the dimensions
# that aren't filterable.
FILTER_DIMENSIONS = {BaseRowType.SOURCE_FIELD, *DIMENSIONS} - EXCLUDE_FILTER_DIMENSIONS

# Dimensions that we are able to restrict querying on
# No values now because we want to give public users access to everything.
AUTHORIZABLE_DIMENSIONS = set()
