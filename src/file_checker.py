# 检查指定的文件，是否符合我们对应化所数据的格式假设
# 预计有 5e7 个文件
# 每个文件压缩前 200KB
# 每个文件压缩后  24KB
import os

IGNORE_FIRST_LINE_CHECK = True

# 读入一个文件，并删除其中的所有空行
def read_file(filename):
    assert os.path.isfile(filename)
    lines = []
    for line in open(filename):
        line = line.strip()
        if line != "":
            lines.append(line)
    return lines



# 检查头部数据正确性
# header_info = ontent_check(content)
# header_info： 错误信息
def header_check(content: list[str]):
    if not IGNORE_FIRST_LINE_CHECK: # 跳过首行检查
        front_line = content[0]     # 检查首行正确性
        if not front_line.startswith("LAMMPS data file via write_data, version 12"):
            return "front_line_error"
    data_size_line = content[1] # 检查数据量行的正确性
    if not data_size_line.endswith(" atoms"):
        return "data_size_line_error"
    return "" # 没有任何错误



# 分割数据，将数据分给为三部分
def split_content(content: list[str]):
    part_list = []
    part_now  = []
    for line in content:
        if line.startswith("Atoms") or line.startswith("Bonds") or line.startswith("Velocities") or line.startswith("Angles"):
            # append data and clear part_now
            if part_now != []:
                part_list.append(part_now)
            part_now = [line]
        else:
            part_now.append(line)
    if part_now != []: # 处理最后一个 block 的内容
        part_list.append(part_now)
    head = part_list[0]
    atom = []
    bond = []
    for part in part_list:
        if part[0].startswith("Atoms"):
            atom = part
        if part[0].startswith("Bonds"):
            bond = part
    return head, atom, bond



# 删除第一行，然后取其他行的内容为 list of list
def get_data_body(part_content: list[str]):
    lines = []
    for i in range(1, len(part_content)):
        line = part_content[i].split()
        if len(line) == 4: # new datas
            lines.append(line)
        elif len(line) == 9: # old datas
            lines.append([line[0]] + line[3:6])
        else:
            assert False
    return lines



# content 为 read_file 函数的返回结果
# 函数返回错误信息
# 如果返回空字符串说明格式正确
def content_check(content: list): # 分离头部数据以及其他数据
    header_content, atom_content, bond_content = split_content(content)
    header_info = header_check(header_content) # 检查头部信息
    if header_info != "":
        return header_info, None, None
    if len(atom_content) != len(bond_content): # 检查配对是否正确
        return "length_not_match", None, None
    atom_data = get_data_body(atom_content) # 拆分数据部分
    bond_data = get_data_body(bond_content) 
    if len(atom_data) != len(bond_data):
        return "body_length_not_match", None, None
    return "", atom_data, bond_data # 没有遇到错误



if __name__ == "__main__": # debug
    DIRNOW      = os.path.dirname(os.path.abspath(__file__))
    SAMPLE_FILE = os.path.join(DIRNOW, "data.random_knot_widened_L1000_K0_melt_limit_1")
    lst = read_file(SAMPLE_FILE)
    info, atoms, bonds = content_check(lst)
    print(len(atoms))