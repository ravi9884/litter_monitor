import os
import pickle
from typing import List, Tuple

def get_list(storage_loc: str) -> List[Tuple[int, int, int, int]]:
    """Returns a list of coordinate tuples stored in pickle file. These were the objects found in previous run

    Args:
        storage_loc (str): location of the pickle file

    Returns:
        List[Tuple[int, int, int, int]]: If the pickle file is found, returns the coordinates from it, else returns empty list
    """    
    if os.path.isfile(storage_loc):
        with open(storage_loc,'rb') as f:
            return pickle.load(f)
    else:
        return []
    
def write_list(lst: List[Tuple[int, int, int, int]], storage_loc: str) -> None:
    """Writes a list of coordinates for objects found into pickle file

    Args:
        lst (List[Tuple[int, int, int, int]]): A list of coordinates of objects found in the current run
        storage_loc (str): location of the pickle file
    """      
    with open(storage_loc, 'wb') as f:
        pickle.dump(lst, f)