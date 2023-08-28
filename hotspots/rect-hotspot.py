'''

This script will allow one to draw rectangles on an image and upon mouse release it will print the
upper left corner (x,y) and the lower right corner (x,y) values along with the scaled values.

usage: python rect-hotspot.py --image-path ../images/8x8matrix_expansion.png --width 600 --show-hotspots

usage:
python rect-hotspot.py --read-only --image ../images/8x8matrix_expansion.png --width 600 --show-hotspots --filename 8x8-matrix-hotspots.csv


Right click in the Rectangle hotspot to remove
Shift Right Click in the Rectange to get the CSV index of that box

To determine if point is in rectange:
def is_point_in_box(x1, y1, x2, y2, x, y):
    return (x1 <= x <= x2) and (y1 <= y <= y2)

keep in mind the coordinates may need to be scaled if you are using scaled coordinates.
'''
import argparse
import imutils
import cv2
import csv
import numpy as np
from pathlib import Path

WINDOW_NAME = "Image"

# collection of hotspot rectangles.
# [(ul-x, ul-y, lr-x, lr-y), ()]
collected_hotspots = []

# the image to select hotspots on
image = None

# variables
ix = -1
iy = -1
drawing = False

LINE_THICKNESS = 2

def _rectContains(rect, pt):
    """

    :param rect: (ix,iy,x,y)
    :type rect:
    :param pt: (new x,new y)
    :type pt:
    :return:
    :rtype:
    """
    logic = rect[0] < pt[0] < rect[2] and rect[1] < pt[1] < rect[3]
    return logic


def draw_reactangle_with_drag(event, x, y, flags, param):
    global ix, iy, drawing, image
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix = x
        iy = y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            image2 = read_image()
            cv2.rectangle(image2, pt1=(ix, iy), pt2=(x, y), color=(0, 255, 255), thickness=LINE_THICKNESS)
            image = image2

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(image, pt1=(ix, iy), pt2=(x, y), color=(0, 255, 255), thickness=LINE_THICKNESS)
        collected_hotspots.append((ix, iy, x, y))
        image = read_image()


def mouse_events(event, x, y,
                 flags, param):
    global image
    draw_reactangle_with_drag(event, x, y, flags, param)

    if event == cv2.EVENT_RBUTTONDOWN:
        for i, rect in enumerate(collected_hotspots):
            if _rectContains(rect, (x, y)):
                if flags & cv2.EVENT_FLAG_SHIFTKEY:
                    print(f"Rectangle CSV Index: {i+1}") # +1 for the header row
                else:
                    del collected_hotspots[i]
                    image = read_image()
                break

    if show_hotspots:
        show_collected_hotspots()

    cv2.imshow(WINDOW_NAME, image)


def show_collected_hotspots():
    global image
    for points in collected_hotspots:
        ix = int(points[0])
        iy = int(points[1])
        x = int(points[2])
        y = int(points[3])

        cv2.rectangle(image, pt1=(ix, iy), pt2=(x, y), color=(255, 0, 0), thickness=LINE_THICKNESS)


def read_image():
    if mask_transparent:
        _image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        # make mask of where the transparent bits are
        trans_mask = _image[:, :, 3] == 0

        # replace areas of transparency with white and not transparent
        _image[trans_mask] = [255, 255, 255, 255]
        # new image without alpha channel...
        # new_img = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    else:
        _image = cv2.imread(image_path)
    _image = imutils.resize(_image, width, height)
    return _image


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--image-path", type=str, required=True, help="Path to the image to load")
    ap.add_argument("--width", type=int, required=False, default=None, help="Resize image to specified width")
    ap.add_argument("--height", type=int, required=False, default=None, help="Resize image to specified height")

    ap.add_argument("--filename", required=False, default="None",
                    help="Optional. Filename to save hotspot data if provided")
    ap.add_argument("--mask-transparent", action='store_true',
                    help="If the image has a transparent background, map the transparent background to white")
    ap.add_argument("--show-hotspots", action='store_true',
                    help="If present, then always show collected hotspots on the image")
    ap.add_argument("--read-only", action='store_true', help="If present, will not update the file")
    ap.add_argument("--unnormalized", action='store_true', help="If present, will not normalize the coordiates but instead provide exact image size coordinates")

    args = vars(ap.parse_args())

    image_path = args['image_path']
    width = args['width']
    height = args['height']
    filename = args['filename']
    mask_transparent = args['mask_transparent']
    show_hotspots = args['show_hotspots']
    read_only = args['read_only']
    unnormalized = args['unnormalized']

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WINDOW_NAME, mouse_events)

    image = read_image()
    print(f"Image Shape: {image.shape}")

    if filename is not None:
        if Path(filename).exists():
            # read in the hotspot data
            with open(filename, "r") as f:
                csv_reader = csv.reader(f, delimiter=',')
                for row in csv_reader:
                    try:
                        row = list(np.float_(row))
                        ix = int(row[0] * image.shape[1])
                        iy = int(row[1] * image.shape[0])
                        x = int(row[2] * image.shape[1])
                        y = int(row[3] * image.shape[0])
                        collected_hotspots.append((ix, iy, x, y))
                    except:
                        # probably header
                        pass

    if show_hotspots:
        show_collected_hotspots()
    cv2.imshow(WINDOW_NAME, image)

    cv2.waitKey(0)

    if read_only is False and filename is not None:
        print(f"Writing coordinates to file: {filename}")
        with open(filename, "w") as f:
            hotsport_writer = csv.writer(f, delimiter=',')
            hotsport_writer.writerow(["upper_left_x", "upper_left_y", "lower_right_x", "lower_right_y"])
            for i, data in enumerate(collected_hotspots):
                if unnormalized:
                    norm_ix = data[0]
                    norm_iy = data[1]
                    norm_x = data[2]
                    norm_y = data[3]
                else:
                    norm_ix = data[0] / image.shape[1]
                    norm_iy = data[1] / image.shape[0]
                    norm_x = data[2] / image.shape[1]
                    norm_y = data[3] / image.shape[0]
                hotsport_writer.writerow([norm_ix, norm_iy, norm_x, norm_y])

    cv2.destroyAllWindows()