from config.bw.aggregation import DIMENSIONS
from config.bw.datatypes import BaseRowType

# Dimensions that should not be filterable for users
EXCLUDE_FILTER_DIMENSIONS = set()

# List of dimensions that will display in the filter dropdown and be filterable.
# Include the source dimension and any others in AQT, exclude the dimensions
# that aren't filterable.
FILTER_DIMENSIONS = {BaseRowType.SOURCE_FIELD, *DIMENSIONS} - EXCLUDE_FILTER_DIMENSIONS

# Dimensions that we are able to restrict querying on
AUTHORIZABLE_DIMENSIONS = set()
