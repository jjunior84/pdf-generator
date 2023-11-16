from io import BytesIO
from typing import Any, Dict, List

import streamlit as st
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile

MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
MAX_COLUMNS: int = 4


def get_next_position(max_column: int):
    """Generator with logic to return row, col to positioning next element

    Args:
        max_column (int): maximum number of columns to be considered

    Yields:
        tuple[int, int]: row, column positioning
    """
    row, col = 0, 0
    while True:
        yield row, col
        col += 1
        if col == max_column:
            col = 0
            row += 1


next_position = get_next_position(MAX_COLUMNS)
containers: Dict[int, Any] = {}


def get_container(row: int) -> Any:
    """Get or generate streamlit container based on row
    Args:
        row (int): which row container represent

    Returns:
        Any: streamlit container, it´s proto
    """
    if not containers.get(row):
        containers[row] = st.container()
    return containers[row]


def load_image(image_file: UploadedFile):
    """Load image on the web app to right container and column position

    Args:
        image_file (UploadedFile): Image to load on container
    """
    row, col = next(next_position)

    container = get_container(row)
    with container:
        cols[col].image(image_file)


def generate_pdf(images: List[UploadedFile]):
    """Get images and generate PDF.

    Returns:
        bytes: return buffered file to be saved
    """
    buf = BytesIO()
    if len(images) > 0:
        Image.open(images[0]).save(
            buf,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=[Image.open(image) for image in images[1:]],
        )
    byte_im = buf.getvalue()
    return byte_im


st.set_page_config(layout="wide", page_title="PDF Generator from Images")
cols = st.columns(MAX_COLUMNS)

with st.container():
    st.write("### PDF Generator from Images")
    st.write(
        ":dog: Load images and save to PDF. This code is open source and \
            available [here](https://github.com/jjunior84/pdf-generator) on \
                GitHub. :grin:"
    )

st.sidebar.write("## Upload and download :gear:")

images_uploaded = st.sidebar.file_uploader(
    "Upload an image(s)", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

if images_uploaded:
    for image in images_uploaded:
        if image.size > MAX_FILE_SIZE:
            st.error(
                "The uploaded file is too large. Please upload an images smaller than 5MB."
            )
        else:
            load_image(image)

    st.sidebar.markdown("\n")
    st.sidebar.download_button(
        "Download PDF", generate_pdf(images_uploaded), "name.pdf", "application/pdf"
    )
