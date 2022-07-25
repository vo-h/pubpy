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


# def temperature_pipeline_1(annotation: str, heading_type: str, conversion_technique: int = 1) -> Tuple[dict, dict, dict, dict, list]:
#     """The simplest of pipelines to get temperate data. Throw away data that:
#        - have multiple cid references
#        - have multiple reports
#        - have dirty un-programmatically parsable report string.

#     Args:
#         annotation (str): something like 'Boiling Point'.
#         heading_type (str): something like 'Compound'.

#     Returns:
#         Tuple[dict, dict, dict, dict, list]: (
#             dict_clean_data,
#             dict_with_dirty_report_string,
#             dict_with_multiple_reports,
#             dict_with_multiple_cids,
#             list_of_data_that_dont_have_cid_or_data
#         )
#     """
#     total_pages = utils.get_total_pages(annotation, heading_type)

#     clean_data = {}
#     mul_cid_data = {}
#     mul_report_data = {}
#     dirty_str_data = {}
#     first_err_data = []

#     for page_no in range(1, total_pages + 1):

#         raw_data, err_data = utils.get_raw_data_by_page(annotation, heading_type, page_no)
#         one_cid, mul_cid = sep.separate_by_cid(raw_data)
#         one_report, mul_report = sep.separate_by_reports(one_cid)
#         clean_str, dirty_str = sep.separate_by_temperature_data_string(one_report, conversion_technique)

#         clean_data = {**clean_data, **clean_str}
#         mul_cid_data = {**mul_cid_data, **mul_cid}
#         mul_report_data = {**mul_report_data, **mul_report}
#         dirty_str_data = {**dirty_str_data, **dirty_str}
#         first_err_data.append(err_data)

#     return clean_data, dirty_str_data, mul_report_data, mul_cid_data, first_err_data


# def temperature_pipeline_2(annotation: str, heading_type: str) -> Tuple[dict, dict, dict, dict, list]:
#     """The simplest of pipelines to get temperate data. Throw away data that:
#        - have multiple cid references
#        - have multiple reports
#        - have dirty un-programmatically parsable report string.

#     Args:
#         annotation (str): something like 'Boiling Point'.
#         heading_type (str): something like 'Compound'.

#     Returns:
#         Tuple[dict, dict, dict, dict, list]: (
#             dict_clean_data,
#             dict_with_dirty_report_string,
#             dict_with_multiple_reports,
#             dict_with_multiple_cids,
#             list_of_data_that_dont_have_cid_or_data
#         )
#     """
#     total_pages = utils.get_total_pages(annotation, heading_type)

#     clean_data = {}
#     mul_cid_data = {}
#     mul_report_data = {}
#     mul_dp_data = {}
#     dirty_str_data = {}
#     first_err_data = []

#     for page_no in range(1, total_pages + 1):

#         raw_data, err_data = utils.get_raw_data_by_page(annotation, heading_type, page_no)
#         one_cid, mul_cid = sep.separate_by_cid(raw_data)
#         one_report, mul_report = sep.separate_by_reports(one_cid)
#         one_dp, mul_dp = sep.separate_by_data_points(one_report)
#         clean_str, dirty_str = sep.separate_by_temperature_data_string(one_dp, 3)

#         clean_data = {**clean_data, **clean_str}
#         mul_cid_data = {**mul_cid_data, **mul_cid}
#         mul_report_data = {**mul_report_data, **mul_report}
#         mul_dp_data = {**mul_dp_data, **mul_dp}
#         dirty_str_data = {**dirty_str_data, **dirty_str}
#         first_err_data.append(err_data)

#     return clean_data, dirty_str_data, mul_dp_data, mul_report_data, mul_cid_data, first_err_data
