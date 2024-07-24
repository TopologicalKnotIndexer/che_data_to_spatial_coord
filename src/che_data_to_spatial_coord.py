import os
from file_zip import get_pos_list
DIRNOW      = os.path.dirname(os.path.abspath(__file__)) # 加载测试数据
SAMPLE_FILE = os.path.join(DIRNOW, "data.random_knot_widened_L1000_K0_melt_limit_1")

# 给定一个存储分子数据的文件，返回一个 list of list[3] 作为空间数据
def che_data_to_spatial_coord(filepath: str) -> list[list]:
    return get_pos_list(filepath)

if __name__ == "__main__":
    assert len(che_data_to_spatial_coord(SAMPLE_FILE)) == 1000