import cv2
import os
from pathlib import Path
import numpy as np
import logging
import re

logging.basicConfig(level=logging.INFO)


def check_lists_for_mismatch(lst_1: list, lst_2: list) -> None:
    lst_1 = [re.sub(r"(pm|ym)", "", x) for x in lst_1]
    lst_2 = [re.sub(r"(pw|yw)", "", x) for x in lst_2]

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

    images_mark_list = sorted([str(x) for x in images_mark_list])
    images_clean_list = sorted([str(x) for x in images_clean_list])

    check_lists_for_mismatch(images_mark_list, images_clean_list)

    if len(images_mark_list) != len(images_clean_list):
        logging.error(f"the number of images in the folders is not the same")
        raise AssertionError(f"the number of images in the folders is not the same")

    logging.info(f" {len(images_mark_list)} images with markups found")
    logging.info(f" {len(images_clean_list)} images without markups found")

    return images_mark_list, images_clean_list


def open_image(image: str) -> np.ndarray:
    img = cv2.imread(image)

    return img


def create_folders(path_to_save: Path) -> None:
    main_path = path_to_save

    sub_dir1 = main_path / "images"
    sub_dir2 = main_path / "labels"

    main_path.mkdir(parents=True)
    sub_dir1.mkdir()
    sub_dir2.mkdir()

    logging.info(f"Create dir: {str(main_path)} and sub dirs: {sub_dir1} & {sub_dir2}")


def markup_images(path_to_folder: Path, save_path: Path) -> None:
    image_paths_mark, images_clean = images_collector(path_to_folder)
    print(image_paths_mark[0])
    print(images_clean[0])

    if not save_path.exists():
        create_folders(save_path)

    for path in image_paths_mark:
        markups = []
        img = open_image(path)

        if img is None:
            logging.info(f"Error: Could not load image from {path}")
        else:
            logging.info(f"load image from path: {path}")

        cv2.imshow(f"{path}", img)

        if cv2.waitKey(0) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    path = Path("./data/good")
    save_path = Path("./data/markups")
    markup_images(path, save_path)
