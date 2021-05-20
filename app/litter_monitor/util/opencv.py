import os
import cv2
import logging
from typing import Tuple, List
import numpy as np
from litter_monitor.util import image

def get_base_images(mask_filename: str, ref_filename: str, snapshot_filename: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """reads base images from file system and returns them as numpy array

    Args:
        mask_filename (str): Filename for the mask that specifies which area to monitor
        ref_filename (str): Filename of reference file without any litter
        snapshot_filename (str): Current snapshot file from the camera

    Raises:
        Exception: Raises exception if any of the file is not found

    Returns:
        Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]: numpy array of the input images
    """ 
    logging.info(f'opening mask file {mask_filename}')
    #imread doesn't raise error when the file is not found
    if not os.path.isfile(mask_filename):
        raise Exception(f'{mask_filename} is not found')

    mask_image = cv2.imread(mask_filename, 0)
    _,mask_t=cv2.threshold(mask_image, 127, 255, cv2.THRESH_BINARY) 

    logging.info(f'opening reference file {ref_filename}')
    if not os.path.isfile(ref_filename):
        raise Exception(f'{ref_filename} is not found')    
    ref_image = cv2.imread(ref_filename)

    logging.info(f'opening snapshot file {snapshot_filename}')
    if not os.path.isfile(snapshot_filename):
        raise Exception(f'{snapshot_filename} is not found')    
    snapshot_image = cv2.imread(snapshot_filename)
    return mask_t, ref_image, snapshot_image

def get_matched_objects(contours: List[np.ndarray], hierarchy: np.ndarray, existing_objects: List[Tuple[int, int, int, int]]) -> Tuple[List[Tuple[int, int, int, int]], List[Tuple[int, int, int, int]]]:
    matched_objects = []
    all_objects = []
    for i, c in enumerate(contours):
        if hierarchy[0][i][3] == -1:
            contours_poly = cv2.approxPolyDP(c, 3, True)
            brect = cv2.boundingRect(contours_poly)
            all_objects.append(brect)
            if image.almost_same(brect, existing_objects):
                matched_objects.append(brect)

    return all_objects, matched_objects


def identify_objects(inputCopy2: np.ndarray, boundRect: List[Tuple[int, int, int, int]] ) -> Tuple[List[np.ndarray], np.ndarray]:
    crop_images = []
    im = inputCopy2
    for i in range(len(boundRect)):
        #print(boundRect[i])
        color = (0, 255, 0)
        x1 = int(boundRect[i][0])
        y1 = int(boundRect[i][1])
        x2 = int(boundRect[i][0] + boundRect[i][2])
        y2 = int(boundRect[i][1] + boundRect[i][3])
        crop_img = inputCopy2.copy()[y1:y2+5, x1:x2+5]
        crop_images.append(crop_img)
        im = cv2.rectangle(inputCopy2, (x1, y1), (x2, y2), color, 1)
    return crop_images,im