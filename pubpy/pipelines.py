from pubpy import utils
from pubpy import sep_funcs as sep
from typing import Tuple


def temperature_pipeline_1(annotation: str, heading_type: str, total_pages: int = None) -> Tuple[dict, dict, dict, dict, dict, list]:
    """Get all data available with given annotation and heading_type. Then clean
    with the following steps:
        1. Aggregate molecules with multiple records.
        2. Discard those with multiple cids.
        3. Discard those with multiple in-congruent temperatures.

    Args:
        annotation (str): sth like 'Melting Point'
        heading_type (str): sth like 'Compound'
        total_pages (int): if left as None, get all data.

    Returns:
        Tuple[dict, dict, dict, dict, dict, list]: (
            dict_clean_data,
            dict_with_one_cid_each_but_dirty_string,
            dict_with_one_cid_each_but_both_dirty_and_clean_string,
            dict_with_multiple_cid,
            dict_with_all_data_but_those_that_dont_contain_cid_or_name,
            list_of_records_that_dont_contain_cid_or_name
        )
    """

    raw_data, err_data = utils.get_all_raw_data(annotation=annotation, heading_type=heading_type, total_pages=total_pages)
    one_cid, mul_cid = sep.separate_by_cid(raw_data)
    clean_str, dirty_str = sep.separate_by_temperature_string(one_cid)

    return clean_str, dirty_str, one_cid, mul_cid, raw_data, err_data
