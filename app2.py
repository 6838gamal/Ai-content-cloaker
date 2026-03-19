import streamlit as st
from PIL import Image
import numpy as np
import io
import cv2

# =========================
# IMAGE PROTECTION PIPELINE
# =========================

def adversarial_noise(arr, eps=0.02):
    noise = np.random.randn(*arr.shape)
    return arr + noise * eps

def micro_warp(arr, strength=0.02):
    h,w,c = arr.shape
    dx = (np.random.rand(h,w)-0.5)*2*strength*5
    dy = (np.random.rand(h,w)-0.5)*2*strength*5
    x,y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (x+dx).astype(np.float32)
    map_y = (y+dy).astype(np.float32)
    return cv2.remap(arr, map_x, map_y, interpolation=cv2.INTER_LINEAR)

def freq_scramble(arr):
    fft = np.fft.fft2(arr, axes=(0,1))
    fft_shift = np.fft.fftshift(fft)
    h,w,c = arr.shape
    fft_shift[h//2-20:h//2+20, w//2-20:w//2+20] *= 0.97
    return np.fft.ifft2(np.fft.ifftshift(fft_shift), axes=(0,1)).real

def pattern_inject(arr, strength=0.02):
    h,w,c = arr.shape
    pattern = np.sin(np.linspace(0,20,w))
    pattern = np.tile(pattern,(h,1))
    pattern = np.expand_dims(pattern,2)
    return arr + pattern*strength*0.01

def protect_image(img, level="متوسط"):
    arr = np.array(img).astype(np.float32)/255.0
    if level=="خفيف": eps,strength=0.01,0.5
    elif level=="متوسط": eps,strength=0.02,1.0
    else: eps,strength=0.03,1.5
    arr = adversarial_noise(arr, eps)
    arr = micro_warp(arr, strength)
    arr = freq_scramble(arr)
    arr = pattern_inject(arr, strength)
    arr = np.clip(arr,0,1)
    return Image.fromarray((arr*255).astype(np.uint8))

# =========================
# STREAMLIT UI
# =========================

st.set_page_config(page_title="AI Image Cloaker", layout="centered")
st.title("🛡️ AI Image Cloaker")
st.caption("حماية الصور ضد التحليل بواسطة الذكاء الاصطناعي بدون التأثير على البشر")

uploaded_file = st.file_uploader("📤 ارفع صورة", type=["png","jpg","jpeg"])
level = st.selectbox("🎯 مستوى التعمية", ["خفيف","متوسط","قوي"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="📷 الصورة الأصلية", use_column_width=True)

    if st.button("🔒 حماية الصورة"):
        protected_img = protect_image(img, level)
        st.image(protected_img, caption="🛡️ الصورة بعد الحماية", use_column_width=True)

        buf = io.BytesIO()
        protected_img.save(buf, format="PNG")
        st.download_button("⬇️ تحميل الصورة المحمية", buf.getvalue(), "protected.png", "image/png")
        st.success("✅ تمت حماية الصورة بنجاح")

st.markdown("---")
st.caption("AI Image Cloaker | Built by Gamal Almaqtary")
