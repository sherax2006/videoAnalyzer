

# import streamlit as st
# import os
# import cv2
# import tempfile
# from moviepy.editor import VideoFileClip
# from spleeter.separator import Separator
# from PIL import Image

# # App layout setup
# st.set_page_config(page_title="🎬 Interactive Video Analyzer", layout="wide")
# st.title("🎬 Video Analyzer with Audio Separation")

# # Set up directories
# os.makedirs("spleeter_output", exist_ok=True)

# # Sidebar options
# st.sidebar.title("🎛️ Navigation Panel")
# options = ["Original Video", "Extracted Audio", "Separate Vocals & Background", "View Frame"]
# selected_option = st.sidebar.radio("Choose a Feature", options)

# # Upload a video file
# video_file = st.file_uploader("📤 Upload a Video File", type=["mp4", "mov", "avi"])

# if video_file:
#     # Save uploaded file temporarily
#     tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
#     tfile.write(video_file.read())
#     video_path = tfile.name

#     # Extract audio (only once)
#     audio_output_path = "extracted_audio.wav"
#     video_clip = VideoFileClip(video_path)
#     video_clip.audio.write_audiofile(audio_output_path, verbose=False, logger=None)

#     # Handle selections
#     if selected_option == "Original Video":
#         st.subheader("🎞️ Original Video Playback")
#         # Display video in centered column
#         col1, col2, col3 = st.columns([1, 2, 1])
#         with col2:
#             st.video(video_path)

#     elif selected_option == "Extracted Audio":
#         st.subheader("🔊 Audio Extracted from Video")
#         st.audio(audio_output_path, format="audio/wav")

#     elif selected_option == "Separate Vocals & Background":
#         st.subheader("🎤 Separate Foreground (Vocals) and Background (Music)")
#         if st.button("Start Separation"):
#             st.info("🔄 Separating audio, please wait...")
#             separator = Separator('spleeter:2stems')
#             separator.separate_to_file(audio_output_path, "spleeter_output")

#             vocals_path = os.path.join("spleeter_output", "extracted_audio", "vocals.wav")
#             background_path = os.path.join("spleeter_output", "extracted_audio", "accompaniment.wav")

#             if os.path.exists(vocals_path) and os.path.exists(background_path):
#                 st.success("✅ Separation Completed")
#                 st.subheader("🎙️ Foreground (Vocals)")
#                 st.audio(vocals_path, format="audio/wav")

#                 st.subheader("🎼 Background (Music)")
#                 st.audio(background_path, format="audio/wav")
#             else:
#                 st.error("❌ Failed to find separated audio files. Please try again.")

#     elif selected_option == "View Frame":
#         st.subheader("📸 View Specific Frame from Video")
#         cap = cv2.VideoCapture(video_path)
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#         frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
#         st.write(f"Total Frames: {total_frames}, Frame Rate: {frame_rate} fps")

#         frame_slider = st.slider("Choose Frame Number", 0, total_frames - 1, 0, step=1)
#         cap.set(cv2.CAP_PROP_POS_FRAMES, frame_slider)
#         ret, frame = cap.read()
#         if ret:
#             # Resize frame to fit screen (e.g. max width 800 px)
#             max_width = 800
#             height, width, _ = frame.shape
#             if width > max_width:
#                 scale = max_width / width
#                 frame = cv2.resize(frame, (int(width * scale), int(height * scale)))

#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#             col1, col2, col3 = st.columns([1, 2, 1])
#             with col2:
#                 st.image(frame_rgb, caption=f"Frame {frame_slider}", use_container_width=True)
#         else:
#             st.warning("⚠️ Unable to extract frame.")
#         cap.release()

# else:
#     st.info("📂 Please upload a video file to begin.")


import streamlit as st
import os
import cv2
import tempfile
from moviepy.editor import VideoFileClip
from spleeter.separator import Separator
from PIL import Image

# App layout setup
st.set_page_config(page_title="🎬 Interactive Video Analyzer", layout="wide")
st.title("🎬 Video Analyzer with Audio Separation")

# Sidebar options
st.sidebar.title("🎛️ Navigation Panel")
options = ["Original Video", "Extracted Audio", "Separate Vocals & Background", "View Frame"]
selected_option = st.sidebar.radio("Choose a Feature", options)

# Upload a video file
video_file = st.file_uploader("📤 Upload a Video File", type=["mp4", "mov", "avi"])

if video_file:
    # Save uploaded file temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    video_path = tfile.name

    # Extract audio (temporarily)
    audio_output_path = os.path.join(tempfile.gettempdir(), "extracted_audio.wav")
    video_clip = VideoFileClip(video_path)
    video_clip.audio.write_audiofile(audio_output_path, verbose=False, logger=None)

    # Get filename (without extension) for spleeter output folder
    audio_name_only = os.path.splitext(os.path.basename(audio_output_path))[0]
    spleeter_output_dir = os.path.join(tempfile.gettempdir(), "spleeter_output")
    output_audio_folder = os.path.join(spleeter_output_dir, audio_name_only)

    # Create spleeter_output directory
    os.makedirs(spleeter_output_dir, exist_ok=True)

    if selected_option == "Original Video":
        st.subheader("🎞️ Original Video Playback")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.video(video_path)

    elif selected_option == "Extracted Audio":
        st.subheader("🔊 Audio Extracted from Video")
        st.audio(audio_output_path, format="audio/wav")

    elif selected_option == "Separate Vocals & Background":
        st.subheader("🎤 Separate Foreground (Vocals) and Background (Music)")
        if st.button("Start Separation"):
            st.info("🔄 Separating audio, please wait...")
            separator = Separator('spleeter:2stems')
            separator.separate_to_file(audio_output_path, spleeter_output_dir)

            vocals_path = os.path.join(output_audio_folder, "vocals.wav")
            background_path = os.path.join(output_audio_folder, "accompaniment.wav")

            if os.path.exists(vocals_path) and os.path.exists(background_path):
                st.success("✅ Separation Completed")

                st.subheader("🎙️ Foreground (Vocals)")
                st.audio(vocals_path, format="audio/wav")

                st.subheader("🎼 Background (Music)")
                st.audio(background_path, format="audio/wav")
            else:
                st.error("❌ Failed to find separated audio files. Please check the paths or try again.")

    elif selected_option == "View Frame":
        st.subheader("📸 View Specific Frame from Video")
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        st.write(f"Total Frames: {total_frames}, Frame Rate: {frame_rate} fps")

        # Initialize frame state
        if "current_frame" not in st.session_state:
            st.session_state.current_frame = 0

        col_prev, col_slider, col_next = st.columns([1, 4, 1])
        with col_prev:
            if st.button("⬅️ Previous"):
                if st.session_state.current_frame > 0:
                    st.session_state.current_frame -= 1

        with col_next:
            if st.button("Next ➡️"):
                if st.session_state.current_frame < total_frames - 1:
                    st.session_state.current_frame += 1

        with col_slider:
            st.session_state.current_frame = st.slider(
                "Choose Frame Number",
                0,
                total_frames - 1,
                st.session_state.current_frame,
                step=1,
                key="frame_slider"
            )

        cap.set(cv2.CAP_PROP_POS_FRAMES, st.session_state.current_frame)
        ret, frame = cap.read()
        if ret:
            max_width = 800
            height, width, _ = frame.shape
            if width > max_width:
                scale = max_width / width
                frame = cv2.resize(frame, (int(width * scale), int(height * scale)))

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(frame_rgb, caption=f"Frame {st.session_state.current_frame}", use_container_width=True)
        else:
            st.warning("⚠️ Unable to extract frame.")
        cap.release()

else:
    st.info("📂 Please upload a video file to begin.")
