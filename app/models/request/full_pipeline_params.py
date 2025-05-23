from .loading_params import LoadingParams
from .preprocessing_params import PreprocessingParams
from .analysis_params import AnalysisParams


class FullPipelineParams(LoadingParams, PreprocessingParams, AnalysisParams):
    pass
