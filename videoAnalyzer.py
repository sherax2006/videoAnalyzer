import streamlit as st
import os
import cv2
import shutil
from moviepy.editor import VideoFileClip
from spleeter.separator import Separator
import tempfile

st.set_page_config(page_title="Media Analyzer", layout="wide")

st.title("📹 Media Analyzer: Extract Frames & Audio Separation")

# Upload section
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
if uploaded_file:
    # Save uploaded video to temp file
    tdir = tempfile.mkdtemp()
    video_path = os.path.join(tdir, uploaded_file.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Uploaded: {uploaded_file.name}")

    # Show analyze button
    if st.button("Analyze video"):
        # Display uploaded video
        st.subheader("Original Video")
        st.video(video_path)

        # 1️⃣ Extract frames
        st.subheader("Extracted Frames")
        frames_dir = os.path.join(tdir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        cap = cv2.VideoCapture(video_path)
        idx = 0
        saved = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            img_path = os.path.join(frames_dir, f"frame_{idx:06d}.jpg")
            cv2.imwrite(img_path, frame)
            if idx < 5:
                saved.append(img_path)
            idx += 1
        cap.release()
        # display first 5 frames
        cols = st.columns(len(saved))
        for c, img in zip(cols, saved):
            c.image(img, caption=os.path.basename(img), use_column_width=True)
        # zip and download all frames
        zip_frames = os.path.join(tdir, "frames.zip")
        shutil.make_archive(zip_frames.replace('.zip',''), 'zip', frames_dir)
        with open(zip_frames, 'rb') as fp:
            st.download_button("Download all frames (zip)", data=fp, file_name="frames.zip")

        # 2️⃣ Extract audio
        st.subheader("Extracted Audio")
        audio_path = os.path.join(tdir, "audio.mp3")
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path)
        clip.close()
        st.audio(audio_path)
        with open(audio_path, 'rb') as fp:
            st.download_button("Download extracted audio", data=fp, file_name="extracted_audio.mp3")

        # 3️⃣ Separate stems
        st.subheader("Audio Separation")
        sep_dir = os.path.join(tdir, "separated")
        separator = Separator('spleeter:2stems')
        separator.separate_to_file(audio_path, sep_dir)
        vocal = os.path.join(sep_dir, os.listdir(sep_dir)[0], 'vocals.wav')
        accomp = os.path.join(sep_dir, os.listdir(sep_dir)[0], 'accompaniment.wav')
        st.markdown("**Vocals (Foreground)**")
        st.audio(vocal)
        st.download_button("Download vocals", data=open(vocal,'rb'), file_name="vocals.wav")
        st.markdown("**Accompaniment (Background)**")
        st.audio(accomp)
        st.download_button("Download accompaniment", data=open(accomp,'rb'), file_name="accompaniment.wav")

        st.success("Analysis complete!")











