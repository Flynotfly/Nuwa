def update_chat_structure(structure, current_id, new_id, path):
    if current_id:
        current_id = int(current_id)
    new_id = int(new_id)
    if len(path) >= 1 and path[-1] == current_id:
        path = path[:-1]
    # print(f"{structure=}, {current_id=}, {new_id=}, {path=}")
    if current_id is None:
        if not structure:
            structure = [new_id]
            return structure
        item = structure[0]
        if not isinstance(item, list):  # [0, 1, 2] => [[[0, 1, 2], [3]]]
            structure = [[structure, [new_id]]]
            return structure
        #  [[[0], [1]]] => [[[0], [1], [2]]]
        structure[0].append([new_id])
        return structure

    i = 0
    j = 0
    current_list = structure
    while True:
        item = current_list[j]
        # print(f"{item=}, {i=}, {j=}")
        if not isinstance(item, list):
            if item == current_id:
                if j + 1 == len(current_list):
                    current_list.append(new_id)
                    return structure
                elif isinstance(current_list[j + 1], list):
                    current_list = current_list[j + 1]
                    current_list.append([new_id])
                    return structure
                else:
                    cutted = current_list[j + 1 :]
                    del current_list[j + 1 :]
                    current_list.append(list())
                    current_list[-1].append(cutted)
                    current_list[-1].append([new_id])
                    return structure
            if path[i] == item:
                i += 1
                j += 1
                continue
            else:
                raise ValueError(
                    f"Can't update chat structure, path value is {path[i]}, item is {item}"
                )
        else:
            current_list = item
            element_to_find = current_id if i == len(path) else path[i]
            is_finded = False
            for element in current_list:
                if element[0] == element_to_find:
                    current_list = element
                    is_finded = True
                    break
            if not is_finded:
                raise ValueError("Can't update chat structure")
            j = 0
            if current_list[0] == current_id:
                if j + 1 == len(current_list):
                    current_list.append(new_id)
                    return structure
                elif isinstance(current_list[j + 1], list):
                    current_list = current_list[j + 1]
                    current_list.append([new_id])
                    return structure
                else:
                    cutted = current_list[j + 1 :]
                    del current_list[j + 1 :]
                    current_list.append(list())
                    current_list[-1].append(cutted)
                    current_list[-1].append([new_id])
                    return structure
            j += 1
            i += 1
