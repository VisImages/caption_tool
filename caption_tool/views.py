from django.shortcuts import render
import json, os, cv2
from pdf2image import convert_from_path,convert_from_bytes
import numpy as np

def check(request):
    if not os.path.exists("captions//first_confirmed.json"):
        create_confirmed_json()

    if request.GET.get('action') == "change":
        caption = request.GET['new_caption']
        if caption != "":
            change_caption(caption)
        else:
            confirm_caption()

    elif request.GET.get('action') == "confirm":
        confirm_caption()

    result_dict = get_image()
    render_dict = {}
    if result_dict["done"] == True:
        render_dict["caption"] = "No tasks left!"
    else:
        page_num = result_dict["cur_img"]["Page"]
        paper_num = result_dict["paper"]
        caption = result_dict["cur_img"]["Caption"]
        img_id = result_dict["cur_img"]["ImageID"]
        if caption == None:
            caption = "No captions!"
        image_name = paper_num + "-" + str(img_id)

        image_test = convert_from_path('.//media//papers//' + paper_num + '.pdf', dpi=200, first_page=page_num, last_page=page_num)
        page_img = cv2.cvtColor(np.array(image_test[0]), cv2.COLOR_RGB2BGR)
        height, width = page_img.shape[:2]
        bbox = result_dict["cur_img"]["Imagebbox"].copy()
        bbox[0] = max([0, bbox[0] - 0.15])
        bbox[1] = max([0, bbox[1] - 0.15])
        bbox[2] = min([1, bbox[2] + 0.15])
        bbox[3] = min([1, bbox[3] + 0.15])
        tmp_im = page_img[int(height * bbox[1]):int(height * bbox[3]), int(width * bbox[0]):int(width * bbox[2])]
        cv2.imwrite(".//media//image//" + image_name + ".png", tmp_im)

        render_dict["img_src"] = "/media/image/" + image_name + ".png"
        render_dict["pdf_src"] = "/media/papers/" + paper_num + ".pdf&page=" + str(page_num)
        render_dict["caption"] = caption
        render_dict["img_info"] = image_name
        render_dict["tasks_left"] = str(result_dict["remained_tasks"])

    return render(request, "check.html", render_dict)



def get_image():
    to_be_confirmed = []
    with open("captions//first_confirmed.json", "r") as f:
        to_be_confirmed = json.load(f)

    # double check
    if len(to_be_confirmed) < 1:
        return {"done": True, "cur_img": None, "remained_tasks": 0, "paper": None}

    cur_paper_id = to_be_confirmed[0][0]
    cur_img_id = to_be_confirmed[0][1]
    # print(cur_img_id, cur_paper_id)

    cur_img = {}
    with open("captions//" + str(cur_paper_id) +".json", "r") as f:
        all_img_list = json.load(f)
        cur_img = all_img_list[cur_img_id]

    print(cur_img)
    return {"done": False, "cur_img": cur_img, "remained_tasks": len(to_be_confirmed), "paper": str(cur_paper_id)}


def confirm_caption():
    to_be_confirmed = []
    with open("captions//first_confirmed.json", "r") as f:
        to_be_confirmed = json.load(f)

    cur_paper_id = 0
    cur_img_id = 0

    # double check
    if len(to_be_confirmed) < 1:
            return False
    else:
        cur_paper_id = to_be_confirmed[0][0]
        cur_img_id = to_be_confirmed[0][1]
        del(to_be_confirmed[0])
        with open("captions//first_confirmed.json", "w") as f:
            json.dump(to_be_confirmed, f)

    all_img_list = []
    with open("captions//" + str(cur_paper_id) + ".json", "r") as f:
        all_img_list = json.load(f)
        # cur_img = all_img_list[cur_img_id]

    all_img_list[cur_img_id]["first_confirmed"] = True

    with open("captions//" + str(cur_paper_id) + ".json", "w") as f:
        json.dump(all_img_list, f)

    return True

def change_caption(caption_text):
    to_be_confirmed = []
    with open("captions//first_confirmed.json", "r") as f:
        to_be_confirmed = json.load(f)

    cur_paper_id = 0
    cur_img_id = 0

    # double check
    if len(to_be_confirmed) < 1:
        return False
    else:
        cur_paper_id = to_be_confirmed[0][0]
        cur_img_id = to_be_confirmed[0][1]
        del(to_be_confirmed[0])
        with open("captions//first_confirmed.json", "w") as f:
            json.dump(to_be_confirmed, f)

    all_img_list = []
    with open("captions//" + str(cur_paper_id) + ".json", "r") as f:
        all_img_list = json.load(f)
        # cur_img = all_img_list[cur_img_id]

    all_img_list[cur_img_id]["first_confirmed"] = True
    all_img_list[cur_img_id]["Caption"] = caption_text

    with open("captions//" + str(cur_paper_id) + ".json", "w") as f:
        json.dump(all_img_list, f)

    return True

def create_confirmed_json():
    caption_list = os.listdir("captions")

    image_list = []

    for caption_file in caption_list:
        print(caption_file)
        if os.path.exists("media//papers//" + caption_file.split('.')[0] + ".pdf"):
            with open("captions//" + caption_file, "r") as f:
                captions = json.load(f)
                index = 0
                for caption in captions:
                    image_list.append((int(caption_file.split(".")[0]), index))
                    index += 1

    with open("captions//first_confirmed.json", "w") as f:
        json.dump(image_list, f)






