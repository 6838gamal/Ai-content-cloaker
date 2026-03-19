import streamlit as st
from PIL import Image
import numpy as np
import io
import cv2

# =========================
# SMART IMAGE PROTECTION FUNCTIONS
# =========================

def micro_warp(arr, strength=1.0):
    h, w, c = arr.shape
    dx = (np.random.rand(h, w) - 0.5) * strength
    dy = (np.random.rand(h, w) - 0.5) * strength
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (x + dx).astype(np.float32)
    map_y = (y + dy).astype(np.float32)
    return cv2.remap(arr, map_x, map_y, interpolation=cv2.INTER_LINEAR)

def high_freq_noise(arr, intensity=0.5):
    noise = np.random.randn(*arr.shape) * (0.02 * intensity)
    return arr + noise

def jpeg_artifacts(arr, quality=85):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, encimg = cv2.imencode('.jpg', (arr*255).astype(np.uint8), encode_param)
    decimg = cv2.imdecode(encimg, 1).astype(np.float32) / 255.0
    return decimg

def grid_warp(arr, intensity=0.5):
    h, w, c = arr.shape
    grid_size = int(20 + 30 * intensity)
    for i in range(0, h, grid_size):
        for j in range(0, w, grid_size):
            shift_x = int((np.random.rand()-0.5)*5*intensity)
            shift_y = int((np.random.rand()-0.5)*5*intensity)
            arr[i:i+grid_size, j:j+grid_size] = np.roll(
                arr[i:i+grid_size, j:j+grid_size],
                shift=(shift_x, shift_y),
                axis=(0,1)
            )
    return arr

def edge_break(arr, intensity=0.5):
    gray = cv2.cvtColor((arr*255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    noise = (np.random.rand(*edges.shape) < 0.1*intensity)
    edges = edges ^ noise
    edges = edges[..., None]
    return arr * (1 - edges*0.2)

def selective_blur(arr, intensity=0.5):
    gray = cv2.cvtColor((arr*255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    mask = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY_INV,11,2)
    mask = mask.astype(bool)
    blurred = cv2.GaussianBlur(arr, (5,5), 0)
    arr[mask] = blurred[mask]
    return arr

def protect_image_smart(img, intensity=0.5, quality=85):
    arr = np.array(img).astype(np.float32)/255.0

    # === Smart pipeline ===
    arr = micro_warp(arr, 1.5 * intensity)
    arr = grid_warp(arr, intensity)
    arr = edge_break(arr, intensity)
    arr = selective_blur(arr, intensity)
    arr = high_freq_noise(arr, intensity)
    arr = jpeg_artifacts(arr, quality)

    arr = np.clip(arr, 0, 1)
    return Image.fromarray((arr*255).astype(np.uint8))

# =========================
# STREAMLIT UI
# =========================

st.set_page_config(page_title="AI Cloaker Pro", layout="centered")
st.title("🛡️ AI Cloaker Pro – Smart Version")
st.caption("حماية ذكية للصور ضد تحليل الذكاء الاصطناعي مع الحفاظ على شكلها الطبيعي")

# Upload image
uploaded_file = st.file_uploader("📤 ارفع صورة", type=["png","jpg","jpeg"])

# Settings sliders
intensity = st.slider("🎛️ قوة الحماية (Intensity)", 0.0, 1.0, 0.5)
quality = st.slider("🧩 جودة الصورة (JPEG Quality)", 50, 100, 85)

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    col1, col2 = st.columns(2)

    with col1:
        st.image(img, caption="📷 الصورة الأصلية", width=300)

    if st.button("🔒 حماية الصورة"):
        protected = protect_image_smart(img, intensity, quality)
        with col2:
            st.image(protected, caption="🛡️ بعد الحماية", width=300)

        # Download
        buf = io.BytesIO()
        protected.save(buf, format="PNG")
        st.download_button("⬇️ تحميل الصورة", buf.getvalue(), "protected.png", "image/png")

        st.success("✅ تمت حماية الصورة بنجاح")

st.markdown("---")
st.caption("AI Cloaker Pro | Built by Gamal Almaqtary")
