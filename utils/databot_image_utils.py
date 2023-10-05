import streamlit as st
import pandas as pd
import cv2


def is_point_in_box(x1, y1, x2, y2, x, y):
    return (x1 <= x <= x2) and (y1 <= y <= y2)


def find_box(normal_x: float, normal_y: float, df: pd.DataFrame):
    for row in df.iterrows():
        if is_point_in_box(row[1]['upper_left_x'], row[1]['upper_left_y'], row[1]['lower_right_x'],
                           row[1]['lower_right_y'], normal_x, normal_y):
            return row
    else:
        return None


@st.cache_data
def read_hot_spots(csv_filepath: str) -> pd.DataFrame:
    df = pd.read_csv(csv_filepath)
    return df


@st.cache_data
def read_image(image_path: str):
    _image = cv2.imread(image_path)
    im_rgb = cv2.cvtColor(_image, cv2.COLOR_BGR2RGB)
    # _image = imutils.resize(_image, width, height)
    return im_rgb

