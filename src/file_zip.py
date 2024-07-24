# 用于对检查器输出的数据进行压缩
import math
import struct
import os
import sys
from file_checker import read_file, content_check



# 解析原子坐标
def parse_atoms(atoms_list: list[str]):
    dic = {}
    for line in atoms_list:
        idx, xpos, ypos, zpos = line
        idx  = int(idx)    # 原子编号
        xpos = float(xpos) # (x, y, z) 坐标
        ypos = float(ypos)
        zpos = float(zpos)
        dic[idx] = [xpos, ypos, zpos] # 这里应该是 list 而不是 tuple
    return dic



# 确保节点存在性
def alloc(nxt, idx):
    if nxt.get(idx) is None:
        nxt[idx] = []



# 增加一条边
def add_edge(nxt:dict[int, list[int]], id_from:int, id_to:int):
    alloc(nxt, id_from)
    alloc(nxt, id_to)
    if id_to not in nxt[id_from]:
        nxt[id_from].append(id_to)
    if id_from not in nxt[id_to]:
        nxt[id_to].append(id_from)



# 解析化学键，得到邻接表
def parse_bonds(bonds_list: list[str]):
    nxt = {}
    for line in bonds_list:
        _, _, id_from, id_to = line
        id_from = int(id_from)
        id_to   = int(id_to)
        add_edge(nxt, id_from, id_to)
    return nxt



# 在有向图中 DFS 环
def get_loop(nxt):
    vis = {}
    pos_now = 1
    arr = []
    while True:
        assert len(nxt[pos_now]) == 2
        assert vis.get(pos_now) is None
        vis[pos_now] = True # 访问
        arr.append(pos_now) # 追加到 DFS 序
        lpos = nxt[pos_now][0]
        rpos = nxt[pos_now][1]
        if vis.get(lpos) is not None and vis.get(rpos) is not None:
            break
        else:
            minv = math.inf
            if vis.get(lpos) is None: # 向没走过的方向移动
                minv = min(minv, lpos)
            if vis.get(rpos) is None: # 向没走过的方向移动
                minv = min(minv, rpos)
            pos_now = minv
    return arr



# atoms_list, bonds_list 来自 content_check 函数的返回值
def content_pos_list(atoms_list: list[str], bonds_list: list[str]):
    dic = parse_atoms(atoms_list)
    nxt = parse_bonds(bonds_list)
    arr = get_loop(nxt)
    assert len(nxt) == len(arr) and len(dic) == len(nxt)
    pos_list = [] # 坐标序列
    for v in arr:
        pos_list.append(dic[v])
    return pos_list



# 打包坐标序列
def zip_pos_list(pos_list: list[float]) -> bytes:
    bytes_val = b""
    for x, y, z in pos_list:
        bytes_val += struct.pack("d", x) # double value
        bytes_val += struct.pack("d", y)
        bytes_val += struct.pack("d", z)
    return bytes_val



# 获取坐标序列
def get_pos_list(input_path):
    assert os.path.isfile(input_path) # 确保被读取的文件存在
    lst = read_file(input_path)
    info, atoms, bonds = content_check(lst)
    if info != "": # 检查是否有错误
        sys.stderr.write(info + "\n")
        assert False
    return content_pos_list(atoms, bonds)



# 压缩一个文件
def compress_file(input_path: str, output_path: str):
    pos_list = get_pos_list(input_path)
    zip_list = zip_pos_list(pos_list)
    open(output_path, "wb").write(zip_list) # 保存到文件



if __name__ == "__main__":
    DIRNOW      = os.path.dirname(os.path.abspath(__file__))
    SAMPLE_FILE = os.path.join(DIRNOW, "data.random_knot_widened_L1000_K0_melt_limit_1")
    compress_file(SAMPLE_FILE, "tmp.bin")
    # lst = read_file("../data/data.random_knot_widened_L1000_K0_melt_limit_1")
    # info, atoms, bonds = content_check(lst)
    # if info != "":
    #     print("error:", info)
    # else:
    #     pos_list = content_pos_list(atoms, bonds)
    #     zip_list = zip_pos_list(pos_list)
    #     print(pos_list[0])