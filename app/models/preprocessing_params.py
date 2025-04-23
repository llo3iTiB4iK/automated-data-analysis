from typing import Optional, Literal, Union, List

from pydantic import BaseModel, PositiveInt, JsonValue, PositiveFloat, StrictBool

ColumnList = Union[List[str], Literal["*"]]


class PreprocessingParams(BaseModel):
    case_insensitive_columns: ColumnList = []
    clear_punct_columns: ColumnList = []
    clear_digits_columns: ColumnList = []
    row_range_start: Optional[PositiveInt] = None
    row_range_end: Optional[PositiveInt] = None
    row_range_step: Optional[PositiveInt] = None
    index_cols: ColumnList = []
    fill_na_values: JsonValue = None
    mfill: StrictBool = False
    ffill: StrictBool = False
    bfill: StrictBool = False
    drop_na: Optional[Literal['rows', 'columns']] = None
    drop_outliers: StrictBool = False
    outliers_threshold: PositiveFloat = 3.0
    drop_duplicates: StrictBool = False
    duplicate_subset: Optional[ColumnList] = None
    duplicate_keep: Literal['first', 'last', False] = "first"
    datetime_columns: ColumnList = []
    category_columns: ColumnList = []
    join_small_cat: StrictBool = False
    joined_category_name: str = "Other"
    categories_threshold: Optional[PositiveFloat] = None
    scale_numeric: StrictBool = False
    scaling_method: Literal['max_abs_scaling', 'min_max_scaling', 'z_score'] = "max_abs_scaling"
