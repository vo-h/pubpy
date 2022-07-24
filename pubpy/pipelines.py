from pubpy import utils
from typing import Tuple

def temperature_pipeline_1(annotation: str, heading_type: str) -> Tuple[dict, dict, dict, dict, list]:
    """The simplest of pipelines to get temperate data. Throw away data that:
       - have multiple cid references
       - have multiple reports
       - have dirty un-programmatically parsable report string.

    Args:
        annotation (str): something like 'Boiling Point'.
        heading_type (str): something like 'Compound'.

    Returns:
        Tuple[dict, dict, dict, dict, list]: (
            dict_clean_data,
            dict_with_dirty_report_string,
            dict_with_multiple_reports,
            dict_with_multiple_cids,
            list_of_data_that_dont_have_cid_or_data
        )
    """
    total_pages = utils.get_total_pages(annotation, heading_type)

    clean_data = {}
    mul_cid_data = {}
    mul_report_data = {}
    dirty_str_data = {}
    first_err_data = []

    for page_no in range(1, total_pages + 1):

        raw_data, err_data = utils.get_raw_data_by_page(annotation, heading_type, page_no)
        one_cid, mul_cid = utils.separate_by_cid(raw_data)
        one_report, mul_report = utils.separate_by_reports(one_cid)
        clean_str, dirty_str = utils.separate_by_data_string(one_report)

        clean_data = {**clean_data, **clean_str}
        mul_cid_data = {**mul_cid_data, **mul_cid}
        mul_report_data = {**mul_report_data, **mul_report}
        dirty_str_data = {**dirty_str_data, **dirty_str}
        first_err_data.append(err_data)

    return clean_data, dirty_str_data, mul_report_data, mul_cid_data, first_err_data
