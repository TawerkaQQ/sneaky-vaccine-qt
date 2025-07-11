import logging
import os
import re
import time
from pathlib import Path

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO)

MARKUPS = []
IMAGE_INDEX = 0


def check_lists_for_mismatch(lst_1: list, lst_2: list) -> None:
    lst_1 = [re.sub(r"(pm|ym)", "", str(x)) for x in lst_1]
    lst_2 = [re.sub(r"(pw|yw)", "", str(x)) for x in lst_2]

    unique_elements_list = list(set(lst_1) ^ set(lst_2))

    if len(unique_elements_list) > 0:
        logging.info(f"mismatched names: {unique_elements_list}")
        raise AssertionError(f"the number of images in the folders is not the same")


def images_collector(path_to_folder: Path) -> (list[str], list[str]):
    """
    Recursive collecting images if has start with image_pm or image_ym
    """

    if not path_to_folder.exists():
        raise FileNotFoundError(f"Path {path_to_folder} does not exist")
    if not path_to_folder.is_dir():
        raise ValueError(f"Path {path_to_folder} is not a directory")

    image_folders = [x for x in path_to_folder.glob("*") if x.is_dir()]

    images_mark_list = []
    images_clean_list = []
    for folder in image_folders:
        for image in folder.glob("*"):
            if image.is_dir():
                images = image.glob("*.png")
                for img in images:
                    if img.name.startswith(("image_pm", "image_ym")):
                        images_mark_list.append(img)

                    elif img.name.startswith(("image_pw", "image_yw")):
                        images_clean_list.append(img)

            elif image.name.startswith(("image_pm", "image_ym")):
                images_mark_list.append(image)

            elif image.name.startswith(("image_pw", "image_yw")):
                images_clean_list.append(image)

    images_mark_list = sorted([x for x in images_mark_list])
    images_clean_list = sorted([x for x in images_clean_list])

    check_lists_for_mismatch(images_mark_list, images_clean_list)

    if len(images_mark_list) != len(images_clean_list):
        logging.error(f"the number of images in the folders is not the same")
        raise AssertionError(f"the number of images in the folders is not the same")

    logging.info(f" {len(images_mark_list)} images with markups found")
    logging.info(f" {len(images_clean_list)} images without markups found")

    return images_mark_list, images_clean_list


def open_image(image: str) -> np.ndarray:

    img = cv2.imread(image)

    if img is None:
        logging.info("can't load image")

    else:
        return img


def create_folders(path_to_save: Path) -> None:
    main_path = path_to_save

    sub_dir1 = main_path / "images"
    sub_dir2 = main_path / "labels"

    main_path.mkdir(parents=True)
    sub_dir1.mkdir()
    sub_dir2.mkdir()

    logging.info(f"Create dir: {str(main_path)} and sub dirs: {sub_dir1} & {sub_dir2}")


def update_showing_img(img: np.ndarray, wind_name: str, marks: list[tuple[int, int]]):
    for mark in marks:
        img = cv2.circle(
            img, (mark[0], mark[1]), radius=2, color=(0, 0, 255), thickness=5
        )

    cv2.imshow(wind_name, img)


def click_ivent(event, x, y, flags, params):
    image = params[1].copy()
    win_name = params[0]
    if event == cv2.EVENT_LBUTTONDOWN:
        logging.debug(x, " ", y)

        MARKUPS.append((x, y))
        logging.debug(MARKUPS)

        update_showing_img(image, win_name, MARKUPS)


def markup_images(path_to_folder: Path, save_path: Path) -> None:
    global IMAGE_INDEX
    print("-------------------------")
    print("q - exit program")
    print("s - save sample with markups and load next image")
    print("u - update markups on clean image")
    print("d - delete last markup")
    print("n - next photo")
    print("-------------------------")

    image_paths_mark, images_paths_clean = images_collector(path_to_folder)

    if not (image_paths_mark and images_paths_clean):
        logging.info("lists is empty")
        return

    path_clean = images_paths_clean[IMAGE_INDEX]

    img_mark = cv2.imread(image_paths_mark[IMAGE_INDEX])
    img_clean = cv2.imread(path_clean)

    if not save_path.exists():
        create_folders(save_path)

    img_clean_save_path = save_path / "images" / path_clean.name
    img_label_save_path = (
        save_path / "labels" / (path_clean.name.replace(".png", ".txt"))
    )

    cv2.namedWindow(f"with_marks", cv2.WINDOW_NORMAL)
    cv2.namedWindow(f"clean_image", cv2.WINDOW_NORMAL)

    cv2.resizeWindow(f"with_marks", (800, 600))
    cv2.resizeWindow(f"clean_image", (800, 600))

    # for path_mark, path_clean in zip(image_paths_mark, images_paths_clean):
    cv2.imshow(f"with_marks", img_mark)
    cv2.imshow(f"clean_image", img_clean)

    cv2.setMouseCallback(
        f"with_marks", click_ivent, param=("clean_image", img_clean.copy())
    )

    while True:
        key = cv2.waitKey(0) & 0xFF

        if key == ord("q"):
            logging.info(f"exit program")
            cv2.destroyAllWindows()
            return
        elif key == ord("Q"):
            if IMAGE_INDEX == 0:
                logging.info("can't minus, index is 0")
            else:
                IMAGE_INDEX -= 1
                img_mark, img_clean = load_image(
                    image_paths_mark[IMAGE_INDEX],
                    images_paths_clean[IMAGE_INDEX],
                    img_mark,
                    img_clean,
                )
                cv2.imshow(f"with_marks", img_mark)
                cv2.imshow(f"clean_image", img_clean)

        elif key == ord("S"):
            if IMAGE_INDEX >= len(image_paths_mark) - 1:
                logging.info("can't sum, index is max")
            else:
                IMAGE_INDEX += 1

                img_mark, img_clean = load_image(
                    image_paths_mark[IMAGE_INDEX],
                    images_paths_clean[IMAGE_INDEX],
                    img_mark,
                    img_clean,
                )

                cv2.imshow(f"with_marks", img_mark)
                cv2.imshow(f"clean_image", img_clean)

        elif key == ord("s"):
            if not MARKUPS or (len(MARKUPS) != 4):
                logging.error(
                    "The list with labels is empty or contains an invalid number of elements"
                )

            else:
                logging.info(
                    f"save image with label to {img_clean_save_path.parent.parent}"
                )
                cv2.imwrite(img_clean_save_path, img_clean)

                marks_to_save = " ".join([str(x) for x in MARKUPS])
                with open(img_label_save_path, "w") as f:
                    f.write(marks_to_save)

                MARKUPS.clear()
                break

        elif key == ord("u"):
            display_image = img_clean.copy()
            logging.info(f"update image with markups")
            update_showing_img(display_image, f"clean_image", MARKUPS)

        elif key == ord("d"):
            if MARKUPS:
                display_image = img_clean.copy()
                logging.info(f"remove last item from {MARKUPS}")
                MARKUPS.pop(-1)
                logging.info(f"new markups list: {MARKUPS}")

                update_showing_img(display_image, f"clean_image", MARKUPS)
            else:
                logging.info("MARKUPS is clear")

        elif key == ord("n"):
            MARKUPS.clear()
            break


def load_image(
    path_mark: Path, path_clean: Path, mark_old: np.ndarray, clean_old: np.ndarray
):

    img_mark = open_image(str(path_mark))
    img_clean = open_image(str(path_clean))


    if (img_mark is None) or (img_clean is None):
        logging.info(f"Error: Could not load image from {path_mark} or {path_clean}")
        return mark_old, clean_old

    else:
        logging.info(f"load image from path: {path_mark} and {path_clean}")

        return img_mark, img_clean


if __name__ == "__main__":
    path = Path("./data/good")
    save_path = Path("./data/markups")
    markup_images(path, save_path)
