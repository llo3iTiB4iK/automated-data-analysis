from typing import Optional, Literal, Union

from pydantic import BaseModel, PositiveInt, JsonValue, PositiveFloat, Json

ColumnList = Union[Json[list[str]], Literal["*"]]


class PreprocessingParams(BaseModel):
    case_insensitive_columns: ColumnList = []
    clear_punct_columns: ColumnList = []
    clear_digits_columns: ColumnList = []
    row_range_start: Optional[PositiveInt] = None
    row_range_end: Optional[PositiveInt] = None
    row_range_step: Optional[PositiveInt] = None
    index_cols: ColumnList = []
    fill_na_values: JsonValue = None
    mfill: bool = False
    ffill: bool = False
    bfill: bool = False
    drop_na: Optional[Literal['rows', 'columns']] = None
    drop_outliers: bool = False
    outliers_threshold: PositiveFloat = 3.0
    drop_duplicates: bool = False
    duplicate_subset: Optional[ColumnList] = None
    duplicate_keep: Literal['first', 'last', False] = "first"
    datetime_columns: ColumnList = []
    category_columns: ColumnList = []
    join_small_cat: bool = False
    joined_category_name: str = "Other"
    categories_threshold: Optional[PositiveFloat] = None
    scale_numeric: bool = False
    scaling_method: Literal['max_abs_scaling', 'min_max_scaling', 'z_score'] = "max_abs_scaling"
