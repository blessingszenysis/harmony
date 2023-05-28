from models.python.config.pipeline_sources_settings import (
    PipelineSource
)

PIPELINE_CONFIG = [
    PipelineSource(source_id='sim', display_name='SIM'),
    PipelineSource(source_id='sinasc', display_name='SINASC'),
]