import base64
import json
import os
import random
import time

import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response


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
        if not isinstance(item, list):  # [0, 1, 2] => [[0, 1, 2], [3]]
            structure = [structure, [new_id]]
            return structure
        #  [[0], [1]] => [[0], [1], [2]
        structure.append([new_id])
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


def find_branches(structure: list, message_id: int, history: list):
    i = 0
    j = 0
    branches_qnt = []
    chosen_branches = []
    history.append(message_id)
    current_list = structure
    while True:
        item = current_list[j]
        if not isinstance(item, list):
            if not item == history[i]:
                raise ValueError("Can't find branches")
            branches_qnt.append(1)
            chosen_branches.append(0)
            i += 1
            j += 1
            if item == message_id:
                return branches_qnt, chosen_branches
            continue
        else:
            current_list = item
            branches_qnt.append(len(current_list))
            is_finded = False
            for index, element in enumerate(current_list):
                if element[0] == history[i]:
                    current_list = element
                    chosen_branches.append(index)
                    is_finded = True
                    break
            if not is_finded:
                raise ValueError("Can't find branches")
            j = 0
            if current_list[0] == message_id:
                return branches_qnt, chosen_branches
            j += 1
            i += 1


def rebase_branch(structure: list, history: list, branch: int):
    i = 0
    j = 0
    result = []
    current_list = structure
    while i < len(history):
        item = current_list[j]
        if not isinstance(item, list):
            if not item == history[i]:
                raise ValueError("Can't rebase branch")
            result.append(item)
            i += 1
            j += 1
            continue
        else:
            current_list = item
            is_finded = False
            for element in current_list:
                if element[0] == history[i]:
                    current_list = element
                    is_finded = True
                    break
            if not is_finded:
                raise ValueError("Can't rebase branch")
            result.append(current_list[0])
            i += 1
            j = 1
    if len(current_list[j]) - 1 < branch or branch < 0:
        raise ValueError("Branch value is invalid")
    current_list = current_list[j][branch]
    result.append(current_list[0])
    j = 1
    while j < len(current_list):
        item = current_list[j]
        if not isinstance(item, list):
            result.append(item)
            j += 1
            continue
        else:
            current_list = item
            current_list = current_list[-1]
            result.append(current_list[0])
            j = 1
    return result


COMFY_WORKFLOW_PATH = os.path.join(
    settings.BASE_DIR, "workflows", "test_character.json"
)
COMFY_URL = "http://127.0.0.1:8188"


def generate_image(positive_prompt):
    positive_prompt = "Stable_Yogis_SD1.5_Positives, " + positive_prompt
    with open(COMFY_WORKFLOW_PATH, "r") as f:
        workflow = json.load(f)
    seed = random.randint(0, 999_999_999_999_999)
    workflow["3"]["inputs"]["seed"] = seed
    workflow["6"]["inputs"]["text"] = positive_prompt
    payload = {
        "prompt": workflow,
    }
    response = requests.post(
        f"{COMFY_URL}/api/prompt",
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    response_data = response.json()
    prompt_id = response_data["prompt_id"]
    print(f"Prompt submitted. ID: {prompt_id}")

    max_retries = 60
    retry_interval = 1

    for _ in range(max_retries):
        try:
            history_resp = requests.get(
                f"{COMFY_URL}/api/history/{prompt_id}", timeout=5
            )
            history_resp.raise_for_status()
            history = history_resp.json()

            if prompt_id in history:
                prompt_data = history[prompt_id]
                outputs = prompt_data.get("outputs", {})

                # Look for SaveImage node output (node "9" in your case)
                if "9" in outputs and "images" in outputs["9"]:
                    image_info = outputs["9"]["images"][0]
                    filename = image_info["filename"]
                    subfolder = image_info.get("subfolder", "")
                    type_ = image_info.get("type", "output")

                    # Fetch the actual image
                    img_resp = requests.get(
                        f"{COMFY_URL}/view",
                        params={
                            "filename": filename,
                            "type": type_,
                            "subfolder": subfolder,
                        },
                        timeout=10,
                    )
                    img_resp.raise_for_status()

                    image_base64 = base64.b64encode(img_resp.content).decode("utf-8")

                    return {
                        "image_base64": image_base64,
                        "filename": filename,
                    }
                else:
                    raise ValueError("Workflow completed but no image found in outputs")

        except requests.RequestException as e:
            pass

        time.sleep(retry_interval)

    raise TimeoutError("ComfyUI image generation timed out")
