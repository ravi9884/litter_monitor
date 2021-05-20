import sys
import logging
import os
import numpy as np
import cv2
import warnings
import logging
import traceback
import sys
from time import sleep
import requests

from litter_monitor.util import roku as r
from litter_monitor.util import plex as p
from litter_monitor.util import mqtt as m
from litter_monitor.util import storage as s
from litter_monitor.util import fileop
from litter_monitor.util import opencv as o
from litter_monitor.util import image as i


#load environment variables
from dotenv import load_dotenv
load_dotenv()

FORMAT = '%(asctime)-15s %(module)s %(name)-8s %(funcName)20s() %(message)s'
logging.basicConfig(format=FORMAT)
logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'INFO'))


def main():

    if len(sys.argv) != 12:
        print(f'Received only ${len(sys.argv)} parameters')
        [print(x) for x in sys.argv]
        ##print(f'usage {sys.argv[0]} "/home/pi/litter_storage" "http://camerapi/camtest.jpg" "192.168.1.110" "Roku Streaming Stick+" "litter_monitor" "litter_photos" "192.168.1.136" 30')
        print(f'usage {sys.argv[0]} "/storage/litter_monitor http://camerapi/camtest.jpg 192.168.1.108 "55\" TCL Roku TV" baseperry trash 192.168.1.136 60 0730 2130 http://baseperry.augusta.lan:1880/getContext"')
        print(sys.argv)
        exit(1)

    storage_location = sys.argv[1]
    logging.info(f'storage_location is {storage_location}')

    snapshot_url = sys.argv[2] #'http://camerapi/'
    snapshot_remote_filename = snapshot_url.split('/')[-1]

    logging.info(f'snapshot url is {snapshot_url}')
    logging.info(f'snapshot_remote_filename is {snapshot_remote_filename}')


    roku_ip = sys.argv[3] #'192.168.1.110'
    logging.info(f'roku_ip is {roku_ip}')

    if os.environ.get( 'PLEX_USER'):
        plex_user = os.environ['PLEX_USER']
    else:
        logging.info(f'Reading PLEX_USER from secrets file')
        with open('/run/secrets/PLEX_USER') as f:
            plex_user=f.read().strip()
    if os.environ.get( 'PLEX_PASSWD'):
        plex_passwd = os.environ['PLEX_PASSWD']
    else:
        logging.info(f'Reading PLEX_PASSWD from secrets file')
        with open('/run/secrets/PLEX_PASSWD') as f:
            plex_passwd=f.read().strip()

    plex_client_name = sys.argv[4] #'Roku Streaming Stick+'
    logging.info(f'plex_client_name is {plex_client_name}')

    plex_server_name = sys.argv[5] #"litter_monitor"
    logging.info(f'plex_server_name is {plex_server_name}')

    plex_library_name = sys.argv[6] #"litter_photos"
    logging.info(f'plex_library_name is {plex_library_name}')

    mqtt_broker = sys.argv[7] #"192.168.1.136"
    logging.info(f'mqtt_broker is {mqtt_broker}')

    interval = int(sys.argv[8]) #"30"
    logging.info(f'interval is {interval}')

    start_time = int(sys.argv[9]) #"30"
    logging.info(f'start_time is {start_time}')

    end_time = int(sys.argv[10]) #"30"
    logging.info(f'end_time is {end_time}')

    context_url = sys.argv[11] #"30"
    logging.info(f'context_url is {context_url}')

    #automatic
    images_url = "/root/machine-learning-portfolio/litter-monitor/app/resources/images/"
    ref_file_list = [images_url+'base_19_54.jpg',
    images_url+'base_09_39.jpg',
    images_url+'base_15_57.jpg',
    images_url + 'mask.jpg']

    while True:
        plex = p.plex_connection(plex_user, plex_passwd, plex_server_name)
        try:
            cur_time = fileop.get_cur_time_num()
            if cur_time > start_time and cur_time < end_time:
                try:
                    r = requests.get(context_url)
                    context = r.json()
                    if context['litter_monitor']:
                        process_images(storage_location, snapshot_url, snapshot_remote_filename, roku_ip, plex, plex_server_name, plex_library_name, plex_client_name, mqtt_broker, ref_file_list)
                    else:
                        logging.info('litter monitor is paused')
                except Exception as e:
                    #continue processing if there is no context
                    process_images(storage_location, snapshot_url, snapshot_remote_filename, roku_ip, plex, plex_server_name, plex_library_name, plex_client_name, mqtt_broker, ref_file_list)
            else:
                logging.info(f'Outside of normal running hours cur_time: {cur_time}, start_time: {start_time}, end_time: {end_time}')
            sleep(interval)
        except KeyboardInterrupt:
            break
        except Exception as e:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            logging.error(e, exc_info=True)
            sleep(interval)


def process_images(storage_location, snapshot_url, snapshot_remote_filename, roku_ip, plex, plex_server_name, plex_library_name, plex_client_name, mqtt_broker, ref_file_list):
    global f
    images_dir = storage_location +'/images'
    reference_dir = storage_location + '/references'
    data_dir = storage_location + '/data'
    detected_dir = storage_location + '/detected'
    objects_found_dir = storage_location + '/objects_found'
    special_dirs = [images_dir, reference_dir, data_dir, objects_found_dir, detected_dir]

    fileop.format_storage_structure(special_dirs)
    fileop.copy_referenc_files(reference_dir, ref_file_list)

    chosen_ref_filename = fileop.get_closest_file(reference_dir)
    mask_filename = reference_dir + '/mask.jpg'
    data_filename = data_dir + '/found_objects.pkl'
    detected_filename = detected_dir+'/detected.jpg'
    snapshot_filename = images_dir + '/' + snapshot_remote_filename

    fileop.store_current_file(images_dir, snapshot_url)

    mask_image, ref_image, snapshot_image = o.get_base_images(mask_filename, chosen_ref_filename, snapshot_filename)

    # ### Mask the images
    # Lets apply the mask to the 'clean room image' and 'current snapshot image'. This will black out the areas which we don't want to monitor. Areas like sofa which will always be different everytime we take an image should not be used for analysis

    masked_ref_image = cv2.bitwise_and(ref_image, ref_image, mask=mask_image)
    masked_snap_image = cv2.bitwise_and(snapshot_image, snapshot_image, mask=mask_image)

    # ### Gray the images
    # Lets convert the images to grayscale which makes it easier to work with them without having to worry about color channels.

    gray_ref_image = cv2.cvtColor(masked_ref_image, cv2.COLOR_BGR2GRAY)
    gray_snap_image = cv2.cvtColor(masked_snap_image, cv2.COLOR_BGR2GRAY)

    # ### Blur the images
    # We need to smudge the images a bit to get a continuous blob of section that changed. Otherwise, we would get grainy images where individual pixels matched

    filterSize = 5
    ref_median = cv2.medianBlur(gray_ref_image, filterSize)
    snap_median = cv2.medianBlur(gray_snap_image, filterSize)
    ref_median = ref_median.astype('float32')
    snap_median = snap_median.astype('float32')

    # ### Identify the difference
    # The important activity of finding the delta happens here. We subtract the pixel values from reference image to find the pixels that changed in the picture.

    delta_image = np.clip(ref_median - snap_median, 0, 255)
    delta_image = delta_image.astype('uint8')


    # ### Convert greyscale to binary
    # We need to apply a threshold to the image to force the pixel to be either 0 or 255. We can do this with a threshold. Changing the threshold controls which pixels will be highlighted as change and which will be not

    threshValue = 60
    _, binaryImage = cv2.threshold(delta_image, threshValue, 255, cv2.THRESH_BINARY)

    # ### Filter out small areas
    # We have to filter areas that showed up in the image, which are really small. Adjusting the minArea parameter adjusts the size of the object that we can find
    componentsNumber, labeledImage, componentStats, componentCentroids =     cv2.connectedComponentsWithStats(binaryImage, connectivity=4)

    # Set the minimum pixels for the area filter:
    #I set 100 for the remote
    minArea = 100

    # Get the indices/labels of the remaining components based on the area stat
    # (skip the background component at index 0)
    remainingComponentLabels = [i for i in range(1, componentsNumber) if componentStats[i][4] >= minArea]

    # Filter the labeled pixels based on the remaining labels,
    # assign pixel intensity to 255 (uint8) for the remaining pixels
    filteredImage = np.where(np.isin(labeledImage, remainingComponentLabels) == True, 255, 0).astype('uint8')
    i.mdisp(filteredImage, 'Image with changes above 100 pixel area')

    #group nearby polygons into a big polygon
    thresh_gray = cv2.morphologyEx(filteredImage, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51,51)));



    # ### Get all the objects from the image
    # We have to get all the objects from the snapshot image as well as objects that appeared previously. We need the objects we saw earlier to flag them. If an object appears only once, we don't need to flag them. Otherwise, app would start flagging people moving around in the frame
    # Find the big contours/blobs on the filtered image:
    existing_objects = fileop.get_existing_objects(data_filename)
    try:
        _,contours, hierarchy = cv2.findContours(thresh_gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        contours, hierarchy = cv2.findContours(thresh_gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    all_objects, matched_objects = o.get_matched_objects(contours, hierarchy, existing_objects)

    #store the objects found
    fileop.write_existing_objects(data_filename, all_objects)

    cropped_images, final_image = o.identify_objects(snapshot_image.copy(), matched_objects)

    if len(matched_objects) > 0:
        logging.info(f'writing final image to {detected_filename}')
        cv2.imwrite(detected_filename, final_image)
        fileop.stored_cropped_images(objects_found_dir, cropped_images + [final_image])
        logging.info('pickup trash')
        r.launch_app(roku_ip)    
        m.enable_warning()
        p.stream_picture(plex, plex_client_name, plex_library_name)
    else:
        m.disable_warning()


if __name__ == "main":
    main()