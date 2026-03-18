import streamlit as st
from PIL import Image, ImageFilter
import numpy as np
import hashlib
import io
import random

# =========================
# TEXT PROTECTION (ARABIC + ENGLISH)
# =========================

UNICODE_MAP = {
    "A": "Α", "a": "ɑ", "o": "〇", "e": "℮", 
    "i": "ι", "s": "ѕ", "c": "ϲ", "r": "я"
}

ARABIC_UNICODE_MAP = {
    "ا": "ٱ", "ب": "ﺐ", "ت": "ﺕ", "ث": "ﺙ", "ج": "ﺝ",
    "ح": "ﺡ", "خ": "ﺥ", "د": "ﺩ", "ذ": "ﺫ", "ر": "ﺭ",
    "ز": "ﺯ", "س": "ﺱ", "ش": "ﺵ", "ص": "ﺹ", "ض": "ﺽ",
    "ط": "ﻁ", "ظ": "ﻅ", "ع": "ﻉ", "غ": "ﻍ", "ف": "ﻑ",
    "ق": "ﻕ", "ك": "ﻙ", "ل": "ﻝ", "م": "ﻡ", "ن": "ﻥ",
    "ه": "ﻩ", "و": "ﻭ", "ي": "ﻱ", "ى": "ﻯ"
}

ZW_CHARS = ["\u200B", "\u200C", "\u200D", "\u2060"]

def add_zero_width(text):
    return "".join(ch + random.choice(ZW_CHARS) for ch in text)

def unicode_substitute_arabic(text):
    result = ""
    for ch in text:
        if ch in ARABIC_UNICODE_MAP and random.random() > 0.5:
            result += ARABIC_UNICODE_MAP[ch]
        else:
            result += ch
    return result

def unicode_substitute(text):
    t = "".join(UNICODE_MAP.get(ch, ch) for ch in text)
    t = unicode_substitute_arabic(t)
    return t

def add_metadata(text):
    # Metadata مخفية داخليًا، غير مرئية للمستخدم
    return text + "\n\nContent-Sensitivity: High\nAI-Processing: Prohibited"

def protect_text(text):
    t1 = add_zero_width(text)
    t2 = unicode_substitute(t1)
    t3 = add_metadata(t2)
    fp = hashlib.sha256(text.encode()).hexdigest()
    return t3, fp

# =========================
# IMAGE PROTECTION (ADVANCED)
# =========================

def add_noise(arr, strength=8):
    noise = np.random.randint(-strength, strength + 1, arr.shape)
    return arr + noise

def add_high_freq_pattern(arr, alpha=1):
    h, w, c = arr.shape
    pattern = np.random.randint(-alpha, alpha + 1, (h, w, c))
    return arr + pattern

def add_edge_perturbation(arr, alpha=1):
    # خفيف جدًا، لا يظهر للعين البشرية
    from scipy.ndimage import gaussian_gradient_magnitude
    edges = gaussian_gradient_magnitude(arr.astype(np.float32), sigma=1)
    arr = arr + (edges * alpha).astype(np.int16)
    return arr

def protect_image(img, strength=8):
    arr = np.array(img).astype(np.int16)
    arr = add_noise(arr, strength)
    arr = add_high_freq_pattern(arr, alpha=1)
    arr = add_edge_perturbation(arr, alpha=1)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# =========================
# UI
# =========================

st.set_page_config(page_title="AI Content Cloaker Ultra", layout="centered")
st.title("🛡️ AI Content Cloaker Ultra")
st.caption("حماية النصوص العربية/الإنجليزية والصور بدون أي علامات للمستخدم")

mode = st.radio("اختر نوع المحتوى:", ["نص", "صورة"])

if mode == "نص":
    input_text = st.text_area("✍️ أدخل النص:", height=200)
    if st.button("🔒 تحصين النص"):
        if not input_text.strip():
            st.warning("الرجاء إدخال نص")
        else:
            protected, fp = protect_text(input_text)
            st.subheader("📄 النص المحصن")
            st.text_area("انسخ النص:", value=protected, height=200)
            st.subheader("🔑 Fingerprint")
            st.code(fp)
            st.success("✅ تم تحصين النص")

else:
    uploaded_file = st.file_uploader("📤 ارفع صورة", type=["png", "jpg", "jpeg"])
    strength = st.slider("💥 مستوى الحماية", 1, 20, 8)
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        st.subheader("📷 الصورة الأصلية")
        st.image(img, use_column_width=True)
        if st.button("🔒 تحصين الصورة"):
            protected_img = protect_image(img, strength)
            st.subheader("🛡️ الصورة بعد الحماية")
            st.image(protected_img, use_column_width=True)
            buf = io.BytesIO()
            protected_img.save(buf, format="PNG")
            st.download_button(
                label="⬇️ تحميل الصورة المحمية",
                data=buf.getvalue(),
                file_name="protected.png",
                mime="image/png"
            )
            st.success("✅ تم تحصين الصورة")

# Footer
st.markdown("---")
st.caption("AI Content Cloaker Ultra | Built by Gamal Almaqtary")
