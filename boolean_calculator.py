from enum import Enum


class CubeIndex(Enum):
    VAR_NUM = 0
    CUBE_NUM = 1
    CUBES = 2


def not_care_exist(f):
    for cube in f[CubeIndex.CUBES.value]:
        if cube[0] == 0:
            return True
    return False


def choose_most_binate(f):
    result = {}  # this type is {2(index for y) : {1(+y):[0,1,2], -1(-y):[3,4]}, ...}
    for index, cube in enumerate(f[CubeIndex.CUBES.value]):
        for cube_item in cube[1:]:
            absolute_item = abs(cube_item)
            key = cube_item // absolute_item
            if absolute_item in result:
                if key in result[absolute_item]:
                    result[absolute_item][key].append(index)
                else:
                    result[absolute_item][key] = [index]
            else:
                result[absolute_item] = {}
                result[absolute_item][key] = [index]
    unate_cube = {}
    binate_cube = {}
    for k, val in result.items():
        if len(val) == 1:
            for i in val.keys():
                unate_cube[k] = len(val[i])
        else:
            true_form = len(val[1])
            complement_form = len(val[-1])
            binate_cube[k] = abs(true_form - complement_form)
    if len(binate_cube) != 0:
        d = sorted(binate_cube.keys(), key=lambda x: binate_cube[x])
    else:
        d = sorted(unate_cube.keys(), key=lambda x: unate_cube[x])
    return d[0], result[d[0]]


def positive_cofactor(f, var, index_dict):
    cube_list = [k for k in f[CubeIndex.CUBES.value]]
    cube_num = f[CubeIndex.CUBE_NUM.value]
    var_num = f[CubeIndex.VAR_NUM.value]
    for keys, vals in index_dict.items():
        if keys == 1:
            for index in vals:
                cur_cube = cube_list[index]
                cur_cube_size = cur_cube[0]
                cur_cube_vals = cur_cube[1:]
                cur_cube_vals.remove(var)
                cur_cube_size -= 1
                cur_cube_vals.insert(0, cur_cube_size)
                cube_list[index] = cur_cube_vals
        elif keys == -1:
            for index in vals:
                cube_list[index] = 0  # a flag to delete
                cube_num -= 1
    cube_list = [i for i in cube_list if i != 0]
    return var_num-1, cube_num, cube_list


def negative_cofactor(f, var, index_dict):
    cube_list = [k for k in f[CubeIndex.CUBES.value]]
    cube_num = f[CubeIndex.CUBE_NUM.value]
    var_num = f[CubeIndex.VAR_NUM.value]
    for keys, vals in index_dict.items():
        if keys == -1:
            for index in vals:
                cur_cube = cube_list[index]
                cur_cube_size = cur_cube[0]
                cur_cube_vals = cur_cube[1:]
                cur_cube_vals.remove(-var)
                cur_cube_size -= 1
                cur_cube_vals.insert(0, cur_cube_size)
                cube_list[index] = cur_cube_vals
        elif keys == 1:
            for index in vals:
                cube_list[index] = 0  # a flag to delete
                cube_num -= 1
    cube_list = [i for i in cube_list if i != 0]
    return var_num-1, cube_num, cube_list


def and_operation(var, f):
    cube_num = f[CubeIndex.CUBE_NUM.value]
    var_num = f[CubeIndex.VAR_NUM.value]
    result_list = []
    for i in range(cube_num):
        cur_cube = f[CubeIndex.CUBES.value][i]
        cube_size = cur_cube[0]
        cube_vars = cur_cube[1:]
        cube_vars.append(var)
        cube_vars = sorted(cube_vars, key=lambda x: abs(x))
        cube_vars.insert(0, cube_size+1)
        result_list.append(cube_vars)
    return var_num+1, cube_num, result_list


def boolean_operation_or(cube_list1, cube_list2):
    var_num = cube_list1[CubeIndex.VAR_NUM.value]
    cubes = []
    for cube in cube_list1[CubeIndex.CUBES.value]:
        if cube not in cubes:
            cubes.append(cube)
    for cube in cube_list2[CubeIndex.CUBES.value]:
        if cube not in cubes:
            cubes.append(cube)
    cube_num = len(cubes)
    return var_num, cube_num, cubes


def boolean_operation_complement(f):
    if f[CubeIndex.CUBE_NUM.value] == 0:  # empty cube list F = 0
        return f[CubeIndex.VAR_NUM.value], 1, [[0]]
    elif f[CubeIndex.CUBE_NUM.value] == 1:  # contains just one cube
        cube = f[CubeIndex.CUBES.value][0]
        if cube[0] == 0:  # F = 1
            return f[CubeIndex.VAR_NUM.value], 0, [[]]
        else:
            return f[CubeIndex.VAR_NUM.value], len(cube[1:]), [[1, -var] for var in cube[1:]]  # DeMorgan Laws
    elif not_care_exist(f):  # don't care exist, means F = 1, multiple cube exist
        return f[CubeIndex.VAR_NUM.value], 0, [[]]
    else:
        (var, index_dict) = choose_most_binate(f)
        positive_cube = positive_cofactor(f, var, index_dict)
        negative_cube = negative_cofactor(f, var, index_dict)
        p_complement = boolean_operation_complement(positive_cube)
        n_complement = boolean_operation_complement(negative_cube)
        pos_and_res = and_operation(var, p_complement)
        neg_and_res = and_operation(var, n_complement)
        return boolean_operation_or(pos_and_res, neg_and_res)


def is_one(cube_list):
    if cube_list[CubeIndex.CUBE_NUM.value] != 1:
        return False
    else:
        cube = cube_list[CubeIndex.CUBES.value][0]
        return cube[0] == 0


def merge(cube_list1, cube_list2):
    var_num = max(cube_list1[CubeIndex.VAR_NUM.value], cube_list2[CubeIndex.VAR_NUM.value])
    cube_num = cube_list1[CubeIndex.CUBE_NUM.value] + cube_list2[CubeIndex.CUBE_NUM.value]
    merge_cubes = cube_list1[CubeIndex.CUBES.value] + cube_list2[CubeIndex.CUBES.value]
    return var_num, cube_num, merge_cubes


def choose_most_binate_merged(cube_list1, cube_list2):
    merge_cube_list = merge(cube_list1, cube_list2)
    (var, index_dict) = choose_most_binate(merge_cube_list)
    cube_list1_cube_num = cube_list1[CubeIndex.CUBE_NUM.value]
    index_dict1 = {}
    index_dict2 = {}
    for key, vals in index_dict.items():
        for val in vals:
            if val < cube_list1_cube_num:
                if key not in index_dict1:
                    index_dict1[key] = [val]
                else:
                    index_dict1[key].append(val)
            else:
                index_without_cube1_offset = var - cube_list1_cube_num
                if key not in index_dict2:
                    index_dict2[key] = [index_without_cube1_offset]
                else:
                    index_dict2[key].append(index_without_cube1_offset)
    return var, index_dict1, index_dict2


def boolean_operation_and(cube_list1, cube_list2):
    # if one of cube is 0, return 0
    if cube_list1[CubeIndex.CUBE_NUM.value] == 0 or cube_list2[CubeIndex.CUBE_NUM.value] == 0:
        return max(cube_list1[CubeIndex.VAR_NUM.value], cube_list2[CubeIndex.VAR_NUM.value]), 0, [[]]
    elif is_one(cube_list1) or not_care_exist(cube_list1):  # in one of cube's value is 1, return another cube
        return cube_list2
    elif is_one(cube_list2) or not_care_exist(cube_list2):
        return cube_list1
    else:
        #  index_dict1 is var's index in cube_list1, index_dict2 is var's index in cube_list2
        (var, index_dict1, index_dict2) = choose_most_binate_merged(cube_list1, cube_list2)
        positive_cube1 = positive_cofactor(cube_list1, var, index_dict1)
        negative_cube1 = negative_cofactor(cube_list1, var, index_dict1)
        positive_cube2 = positive_cofactor(cube_list2, var, index_dict2)
        negative_cube2 = negative_cofactor(cube_list2, var, index_dict2)
        positive_merge_cube = boolean_operation_and(positive_cube1, positive_cube2)
        negative_merge_cube = boolean_operation_and(negative_cube1, negative_cube2)
        pos_and_res = and_operation(var, positive_merge_cube)
        neg_and_res = and_operation(var, negative_merge_cube)
        return boolean_operation_or(pos_and_res, neg_and_res)
