import requests
import time
from functools import wraps
import xlwt

"""
修补 bj_area_tab 中经纬度数据. 高德 api 中没有关于台湾的经纬度信息.
导出全国省市区的 code 和对应的 name 到 excel
"""


rsp_data = requests.get(
    'https://restapi.amap.com/v3/config/district?keywords=中国&subdistrict=3&key=c185899d1dda52ba930c7ecdb3774df1'
)


def get_running_time(func):
    @wraps(func)
    def inner(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time()
        print('the {} running time is {}'.format(func.__name__, (end_time - start_time)))

        return res

    return inner


def data_processing(source_data):
    province_source_data_list = source_data["districts"][0]["districts"]
    p_dict = {}
    c_dict = {}
    d_dict = {}
    for p in province_source_data_list:
        # province
        p_dict[p["adcode"]] = {"name": p["name"], "center": p["center"].split(",")}
        for c in p["districts"]:
            # city
            c_dict[c["adcode"]] = {"name": c["name"], "center": c["center"].split(",")}
            for d in c["districts"]:
                # district
                d_dict[d["adcode"]] = {"name": d["name"], "center": d["center"].split(",")}
    p_dict.update(c_dict)
    p_dict.update(d_dict)

    return p_dict


@get_running_time
def export_excel(source_data):
    """ 导出全国 area_code 数据到 excel """

    wb = xlwt.Workbook(encoding='ascii')
    sheet1 = wb.add_sheet('area_code')
    # 标题行
    sheet1.write(0, 0, 'province_code')
    sheet1.write(0, 1, 'province_name')
    sheet1.write(0, 2, 'city_code')
    sheet1.write(0, 3, 'city_name')
    sheet1.write(0, 4, 'region_code')
    sheet1.write(0, 5, 'region_name')

    i = 0
    province_source_data_list = source_data["districts"][0]["districts"]
    for p in province_source_data_list:
        # province
        for c in p["districts"]:
            # city
            for d in c["districts"]:
                # district
                i += 1
                sheet1.write(i, 0, p["adcode"])
                sheet1.write(i, 1, p["name"])
                sheet1.write(i, 2, c["adcode"])
                sheet1.write(i, 3, c["name"])
                sheet1.write(i, 4, d["adcode"])
                sheet1.write(i, 5, d["name"])
    wb.save('area_code.xls')
    return "ok"


if __name__ == "__main__":
    source_data_from_api = rsp_data.json()
    print("-----------------start----------------")
    tmp_data = data_processing(source_data_from_api)
    res = export_excel(source_data_from_api)
    print(res)
    print("-----------------end----------------")
