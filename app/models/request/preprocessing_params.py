from typing import Optional, Literal, Union, Type

from pydantic import BaseModel, PositiveInt, JsonValue, PositiveFloat, Field, field_validator, constr
from sklearn.base import TransformerMixin
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, StandardScaler

from app.errors import ParameterError

SCALER_CLASSES: dict[str, Type[TransformerMixin]] = {
    "max_abs_scaling": MaxAbsScaler,
    "min_max_scaling": MinMaxScaler,
    "z_score": StandardScaler,
}

ColumnList = Union[str, list[str], Literal["*"]]


class PreprocessingParams(BaseModel):
    make_copy: bool = False
    case_insensitive_columns: ColumnList = Field(default_factory=list)
    clear_punct_columns: ColumnList = Field(default_factory=list)
    clear_digits_columns: ColumnList = Field(default_factory=list)
    row_range_start: Optional[PositiveInt] = None
    row_range_end: Optional[PositiveInt] = None
    row_range_step: Optional[PositiveInt] = None
    index_cols: ColumnList = Field(default_factory=list)
    fill_na_values: JsonValue = None
    mfill: bool = False
    ffill: bool = False
    bfill: bool = False
    drop_na: Optional[Literal['rows', 'columns']] = None
    drop_outliers: bool = False
    outliers_threshold: PositiveFloat = 3.0
    drop_duplicates: bool = False
    duplicate_subset: ColumnList = Field(default_factory=list)
    duplicate_keep: Literal['first', 'last', False] = "first"
    datetime_columns: ColumnList = Field(default_factory=list)
    category_columns: ColumnList = Field(default_factory=list)
    join_small_cat: bool = False
    joined_category_name: str = "Other"
    categories_threshold: Optional[PositiveFloat] = Field(None, lt=1)
    scale_numeric: bool = False
    scaling_method: constr(to_lower=True) = "z_score"

    @field_validator("scaling_method")  # noqa
    @classmethod
    def validate_scaling_method(cls, v: str) -> str:
        if v not in SCALER_CLASSES:
            raise ParameterError("scaling_method", v, list(SCALER_CLASSES.keys()))
        return v

    @property
    def scaler(self) -> TransformerMixin:
        return SCALER_CLASSES[self.scaling_method]()
