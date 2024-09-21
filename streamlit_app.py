import streamlit as st
import cv2
from PIL import Image
import tempfile
import os
import zipfile
from io import BytesIO

# Function to extract all frames from a video
def extract_all_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    
    # Extract all frames
    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        frames.append(img)
    
    cap.release()
    return frames

# Function to save frames to a temporary folder and create a ZIP file
def save_frames_to_zip(frames):
    # Create a BytesIO object to hold the zip in memory
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for idx, frame in enumerate(frames):
            # Save each frame as an image in the zip file
            temp_image = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            frame.save(temp_image.name)
            zip_file.write(temp_image.name, f"frame_{idx+1}.png")
            os.remove(temp_image.name)
    
    zip_buffer.seek(0)  # Move the cursor to the beginning of the buffer
    return zip_buffer

# Streamlit App
st.title("Video to Image Extractor & Downloader")

# Upload video file
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    # Create a temporary file to save the uploaded video
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        video_path = temp_file.name

    # Extract frames from video
    st.write("Extracting all frames from video...")
    frames = extract_all_frames(video_path)

    # Display extracted frames
    st.write(f"Extracted {len(frames)} frames.")
    for idx, frame in enumerate(frames[:10]):  # Display only the first 10 frames as a preview
        st.image(frame, caption=f"Frame {idx+1}")

    # Save frames to a ZIP file
    if st.button("Download All Frames as ZIP"):
        zip_buffer = save_frames_to_zip(frames)
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="extracted_frames.zip",
            mime="application/zip"
        )

    # Cleanup: Delete the temporary video file
    os.remove(video_path)
