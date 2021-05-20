from pytz import timezone
import datetime
import os
import numpy as np
import re
import logging
from typing import List, Tuple
import requests
import shutil
import pickle
import cv2

def get_cur_time_num(time_pattern: str = "%H%M", tz_str = 'EST') -> int:
    tz = timezone(tz_str)
    loc_dt = datetime.datetime.now(tz)
    nw = int(loc_dt.strftime(time_pattern))
    return nw

def get_closest_file(src_dir: str, file_pattern: str = "^base_([0-9]{2}_[0-9]{2}).jpg$", time_pattern: str = "%H%M", tz_str = 'EST', ) -> str:
    """The lighting differs considerably during different times of the day.
    We need multiple base images to compare due to that. This package picks the reference image
    that is closest to the current time

    Returns:
        str: File name that needs to be picked up from the reference section
    """    

    pat = re.compile(file_pattern)
    nw = get_cur_time_num(time_pattern, tz_str)
    filenames = os.listdir(src_dir)
    ls =[]
    for filename in filenames:
        s = pat.search(filename)
        if s:
            logging.info(f'{filename} matched patter {file_pattern}')
            tm = s.groups(1)
            hour,min = tm[0].split('_')
            nbr = int(hour + min)
            ls.append((nbr,filename))

    s = [(x[1], np.abs(nw-x[0])) for x in ls]
    logging.info(f'{s} files were chosen as candidates for closest file')
    if len(s) == 0:
        raise Exception(f'No reference file matched the pattern {file_pattern} in dir {src_dir} with files {filenames}')
    else:
        chosen_file = sorted(s, key=lambda x: x[1])[0][0]
        logging.info(f'{chosen_file} is chosen as closest file')
        return src_dir + '/' + chosen_file

def format_storage_structure(special_dirs: List[str]) -> None:
    """Creates the structure needed for litter monitor in storage location

    Args:
        special_dirs (List[str]): List of directories that need to be created
    """
    def check_and_create(dir):
        if os.path.isdir(dir):
            logging.info(f'{dir} is available')
        else:
            logging.info(f'{dir} is not available. Creating it')
            os.mkdir(dir)

    [check_and_create(x) for x in special_dirs]

def copy_referenc_files(src_dir: str, ref_file_list: List[str]) -> None:
    """Download the reference files to find the difference between base and current dir

    Args:
        src_dir (str): target directory to download the files
        ref_file_list (List[str]): url of files that needed to be downloaded from github
    """    
    def download_file(url):
        filename=url.split('/')[-1]
        dest = src_dir + '/' + filename
        logging.info(f'Copying {url} to {dest}')
        shutil.copy(url, dest)

    [download_file(x) for x in ref_file_list]
    
def download_referenc_files(src_dir: str, ref_file_list: List[str]) -> None:
    """Download the reference files to find the difference between base and current dir

    Args:
        src_dir (str): target directory to download the files
        ref_file_list (List[str]): url of files that needed to be downloaded from github
    """    
    def download_file(url):
        filename=url.split('/')[-1]
        dest = src_dir + '/' + filename
        logging.info(f'Downloading {url} to {dest}')
        response = requests.get(url, stream=True)
        with open(dest, 'wb') as out:
            shutil.copyfileobj(response.raw, out)

def store_current_file(storage_dir: str, snapshot_url: str) -> None:
    download_referenc_files(storage_dir, [snapshot_url])

def get_existing_objects(storage_loc) -> List[Tuple[int, int, int, int]]:
    if os.path.isfile(storage_loc):
        with open(storage_loc,'rb') as f:
            return pickle.load(f)
    else:
        return []
    
def write_existing_objects(storage_loc, ls):
    with open(storage_loc, 'wb') as f:
        pickle.dump(ls, f)
    
def stored_cropped_images(objects_found_dir, cropped_images: List[np.ndarray]) -> None:
    file_base = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    for idx, object in enumerate(cropped_images):
        filename = objects_found_dir +'/'+file_base + '_'+str(idx)+'.jpg'
        print('writing to', filename)
        cv2.imwrite(filename, object)
