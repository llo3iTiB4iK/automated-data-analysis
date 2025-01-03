from errors import ParameterError
from services.helpers import parameter_operations as po, validators as val


def retrieve_positive_number(param_name: str, params: dict, max_value: int | float = float('inf'), number_type: type = float) -> int | float:
    valid_values: list = [f"Any {number_type.__name__} number from interval (0; {str(max_value)}]."]
    condition: callable = lambda value: val.is_positive_number(value, max_value, number_type)
    return po.get_processed_param_value_with_condition(param_name, params, valid_values, condition, number_type)


def retrieve_columns(data: pd.DataFrame, params: dict, columns_key: str) -> list:
    columns_param: str = params.get(columns_key)
    columns: list
    if columns_param == '*':
        columns = data.columns.tolist()
    else:
        try:
            columns = po.process_json_decoded_param_value(columns_key, params, val.validate_columns)
        except TypeError:
            raise ParameterError(columns_key, columns_param, ["string", "array[string]", "*"])
    return columns