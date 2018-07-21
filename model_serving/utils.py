import io

import cv2
import numpy as np
from PIL import Image


def roi_to_rect(roi):
    x = roi[1]
    y = roi[0]
    width = roi[3] - roi[1]
    height = roi[2] - roi[0]
    return x, y, width, height


def rect_to_roi(rect):
    return rect.x, rect.y, rect.x + rect.width, rect.y + rect.height


def bitmask_to_image(x, mode='RGB'):
    img_arr = np.repeat(
        np.expand_dims(x.astype(np.uint8) * 255, axis=2), 3, axis=2)
    img = Image.fromarray(img_arr).convert(mode)
    return img


def load_image_array(path, mode='RGB'):
    with Image.open(path) as image:
        return np.array(image.convert(mode))


def load_bytes_image_array(bytes_data, mode='RGB'):
    bytes_buffer = io.BytesIO(bytes_data)
    with Image.open(bytes_buffer) as image:
        return np.array(image.convert(mode))


def load_bytes_image(bytes_data, mode='RGB'):
    bytes_buffer = io.BytesIO(bytes_data)
    return Image.open(bytes_buffer).convert(mode)


def mask_to_polygon(mask):
    mask = mask.astype(np.uint8) * 255
    # cv2.RETR_EXTERNAL: returns only extreme outer contour
    _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return None

    sequence = []
    xy = np.reshape(contours[0], (-1, 2))

    # avoid degenerate polygon
    if xy.shape[0] <= 2:
        return None

    for x, y in xy:
        sequence.append(x)
        sequence.append(y)

    return sequence


def print_object(o, index=None):
    l = []
    if index:
        l.append('Object #{:2d}'.format(index))
    else:
        l.append('Object:')

    if o.label:
        l.append('label: {}'.format(o.label))

    if o.box:
        l.append('box: (x, y, w, h) = ({x}, {y}, {w}, {h})'.format(
            x=o.box.x, y=o.box.y, w=o.box.width, h=o.box.height))
    print(', '.join(l))