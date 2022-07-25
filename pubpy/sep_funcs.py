import copy
import numpy as np
from typing import Tuple

from pubpy import converters, utils


def separate_by_cid(raw_data: dict) -> Tuple[dict, dict]:
    """Reduce output of get_raw_data_by_page() to only those that are connected to 1 cid ref.

    Args:
        raw_data (dict): output of get_raw_data_by_page()

    Returns:
        Tuple[dict, dict]: dict_with_one_cid, dict_with_multiple_cid
    """

    keys = list(raw_data.keys())
    data = copy.deepcopy(raw_data)

    one_cid = {}
    mul_cid = {}

    for key in keys:
        cids = data[key]["cid"]

        if len(cids) == 1:
            data[key]["cid"] = cids[0]
            one_cid[key] = data[key]
        else:
            mul_cid[key] = data[key]
    return one_cid, mul_cid


def separate_by_temperature_string(raw_data: dict) -> Tuple[dict, dict]:

    keys = list(raw_data.keys())
    data = copy.deepcopy(raw_data)

    clean_data = {}
    dirty_data = {}

    for key in keys:

        data_strs = data[key]["data"]
        temps = []
        pres_refs = []

        for data_str in data_strs:

            if utils.single_record(data_str):
                temp = converters.convert_to_c(data_str, position="start")
                pres = converters.convert_to_atm(data_str)
            if temp is not None:
                temps.append(temp)
                pres_refs.append(pres)

        clean_temp = []
        clean_pres = []

        # Group temperatures according to pressure ref
        for pres in set(pres_refs):

            indices = [ind for ind, val in enumerate(pres_refs) if val == pres]
            matching_temps = [val for ind, val in enumerate(temps) if ind in indices]

            if np.array(matching_temps).std() < 2:
                clean_pres.append(pres)
                clean_temp.append(np.array(matching_temps).mean())

        if len(clean_temp) != 0:
            clean_data[key] = data[key]
            clean_data[key]["data"] = {"temperature": clean_temp, "pressure_ref": clean_pres}
        else:
            dirty_data[key] = data[key]

    return clean_data, dirty_data
