
import streamlit as st
import os
import cv2
import tempfile
from moviepy.editor import VideoFileClip
from spleeter.separator import Separator
import hashlib
import imageio_ffmpeg
from typing import Tuple, Optional

# App layout setup
st.set_page_config(page_title="🎬 Interactive Video Analyzer", layout="wide")
st.title("🎬 Video Analyzer with Audio Separation")

# Sidebar options
st.sidebar.title("🎛️ Navigation Panel")
options = ["Original Video", "Extracted Audio", "Separate Vocals & Background", "View Frame"]
selected_option = st.sidebar.radio("Choose a Feature", options)

# Upload a video file
video_file = st.file_uploader("📤 Upload a Video File", type=["mp4", "mov", "avi"])


def ensure_ffmpeg_available() -> str:
    """Return ffmpeg executable path or empty string if unavailable."""
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return ""


@st.cache_resource(show_spinner=False)
def extract_audio_to_wav(video_bytes: bytes) -> str:
    """Extract audio from video bytes into a cached WAV path in temp.
    Uses a hash of the bytes to avoid re-extraction on reruns.
    """
    # Hash for cache keying and file names
    h = hashlib.sha256(video_bytes).hexdigest()[:16]
    audio_output_path = os.path.join(tempfile.gettempdir(), f"extracted_audio_{h}.wav")
    if os.path.exists(audio_output_path):
        return audio_output_path

    # Write video bytes to a temp mp4
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile_local:
        tfile_local.write(video_bytes)
        video_tmp_path = tfile_local.name

    try:
        clip = VideoFileClip(video_tmp_path)
        clip.audio.write_audiofile(audio_output_path, verbose=False, logger=None)
        clip.close()
        return audio_output_path
    finally:
        try:
            os.remove(video_tmp_path)
        except OSError:
            pass


def probe_video_meta(video_path: str) -> Tuple[int, float]:
    """Return (total_frames, fps) using OpenCV first, then MoviePy fallback."""
    # Try OpenCV with FFMPEG preference
    total_frames: int = 0
    fps: float = 0.0
    try:
        cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
    except Exception:
        cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or 0.0
        cap.release()
    # Fallback via MoviePy if needed
    if total_frames <= 0 or fps <= 0:
        try:
            clip = VideoFileClip(video_path)
            # MoviePy's fps may be None for some sources; guard
            if clip.fps and clip.duration:
                fps = float(clip.fps)
                total_frames = int(round(clip.duration * fps))
            clip.close()
        except Exception:
            pass
    return total_frames, fps


def fetch_frame_rgb(video_path: str, frame_index: int, fps: float) -> Optional["any"]:
    """Fetch a frame as RGB ndarray. Try OpenCV frame-seek, then timestamp seek, then MoviePy fallback.
    Returns None if all methods fail.
    """
    # Try OpenCV exact frame seek (FFMPEG backend preferred)
    try:
        cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
    except Exception:
        cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        # Method 1: set by frame index
        if cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index):
            ok, frame_bgr = cap.read()
            if ok and frame_bgr is not None:
                rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                cap.release()
                return rgb
        # Method 2: set by timestamp in milliseconds
        if fps and fps > 0:
            t_ms = (frame_index / fps) * 1000.0
            _ = cap.set(cv2.CAP_PROP_POS_MSEC, t_ms)
            ok, frame_bgr = cap.read()
            if ok and frame_bgr is not None:
                rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                cap.release()
                return rgb
        cap.release()
    # Fallback: MoviePy get_frame at time
    try:
        if fps and fps > 0:
            t = frame_index / fps
        else:
            t = 0.0
        clip = VideoFileClip(video_path)
        frame_rgb = clip.get_frame(t)
        clip.close()
        return frame_rgb
    except Exception:
        return None


@st.cache_data(show_spinner=False, max_entries=128)
def get_frame_cached(video_path: str, frame_index: int, fps: float):
    return fetch_frame_rgb(video_path, frame_index, fps)

if video_file:
    # Check ffmpeg availability
    ffmpeg_exe = ensure_ffmpeg_available()
    if not ffmpeg_exe:
        st.warning("FFmpeg not found. MoviePy may fail to extract audio. Please install FFmpeg and ensure it's on PATH.")

    # Persist uploaded video to a temp file for playback and frame viewing
    uploaded_bytes = video_file.getvalue()
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_bytes)
    tfile.flush()
    tfile.close()
    video_path = tfile.name

    # Cleanup previously stored temp video if replaced
    prev_path = st.session_state.get("_prev_video_tmp_path")
    if prev_path and prev_path != video_path and os.path.exists(prev_path):
        try:
            os.remove(prev_path)
        except OSError:
            pass
    st.session_state["_prev_video_tmp_path"] = video_path

    if selected_option == "Original Video":
        st.subheader("🎞️ Original Video Playback")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            mime = getattr(video_file, "type", None) or "video/mp4"
            st.video(uploaded_bytes, format=mime, start_time=0)

    elif selected_option == "Extracted Audio":
        st.subheader("🔊 Audio Extracted from Video")
        try:
            audio_output_path = extract_audio_to_wav(uploaded_bytes)
        except Exception as e:
            st.error(f"Audio extraction failed: {e}")
            st.stop()
        st.audio(audio_output_path, format="audio/wav")

    elif selected_option == "Separate Vocals & Background":
        st.subheader("🎤 Separate Foreground (Vocals) and Background (Music)")
        if st.button("Start Separation"):
            # Prepare output paths lazily
            try:
                audio_output_path = extract_audio_to_wav(uploaded_bytes)
            except Exception as e:
                st.error(f"Audio extraction failed: {e}")
                st.stop()

            audio_name_only = os.path.splitext(os.path.basename(audio_output_path))[0]
            spleeter_output_dir = os.path.join(tempfile.gettempdir(), "spleeter_output")
            output_audio_folder = os.path.join(spleeter_output_dir, audio_name_only)
            os.makedirs(spleeter_output_dir, exist_ok=True)

            try:
                with st.spinner("🔄 Separating audio, please wait..."):
                    separator = Separator('spleeter:2stems')
                    separator.separate_to_file(audio_output_path, spleeter_output_dir)
            except Exception as e:
                st.error(f"Audio separation failed: {e}")
                st.stop()

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
        total_frames, frame_rate = probe_video_meta(video_path)
        st.write(f"Total Frames: {total_frames}, Frame Rate: {int(frame_rate)} fps")
        if total_frames <= 0:
            st.warning("⚠️ Video has no readable frames or metadata could not be determined.")
            st.stop()

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

        frame_rgb = get_frame_cached(video_path, st.session_state.current_frame, frame_rate)
        if frame_rgb is not None:
            max_width = 800
            height, width, _ = frame_rgb.shape
            if width > max_width:
                scale = max_width / width
                frame_rgb = cv2.resize(frame_rgb, (int(width * scale), int(height * scale)))
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(frame_rgb, caption=f"Frame {st.session_state.current_frame}", use_column_width=True)
        else:
            st.warning("⚠️ Unable to extract frame via OpenCV/MoviePy.")

else:
    st.info("📂 Please upload a video file to begin.")
