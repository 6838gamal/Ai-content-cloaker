import streamlit as st
from PIL import Image
import numpy as np
import hashlib
import io
import random

# =========================
# TEXT PROTECTION (INVISIBLE, ARABIC + ENGLISH)
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

def add_zero_width(text, probability=0.02):
    return "".join(ch + (random.choice(ZW_CHARS) if random.random() < probability and ch != " " else "") for ch in text)

def unicode_substitute_arabic(text, probability=0.1):
    return "".join(ARABIC_UNICODE_MAP[ch] if ch in ARABIC_UNICODE_MAP and random.random() < probability else ch for ch in text)

def unicode_substitute(text, probability=0.1):
    t = "".join(UNICODE_MAP[ch] if ch in UNICODE_MAP and random.random() < probability else ch for ch in text)
    return unicode_substitute_arabic(t, probability)

def add_metadata(text):
    return text + "\u2060\u2060\nContent-Sensitivity: High\nAI-Processing: Prohibited"

def protect_text(text):
    t1 = add_zero_width(text)
    t2 = unicode_substitute(t1)
    t3 = add_metadata(t2)
    fp = hashlib.sha256(text.encode()).hexdigest()
    return t3, fp

# =========================
# IMAGE PROTECTION (INVISIBLE, ADVERSARIAL)
# =========================

def add_noise(arr, strength=8):
    noise = np.random.randint(-strength, strength, arr.shape)
    return arr + noise

def add_pattern(arr):
    h, w, c = arr.shape
    for i in range(0, h, 10):
        arr[i:i+1, :, :] = arr[i:i+1, :, :] * 0.98  # خفيف جدًا، غير مرئي للعين
    return arr

def protect_image(img, strength=8):
    arr = np.array(img).astype(np.int16)
    arr = add_noise(arr, strength)
    arr = add_pattern(arr)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# =========================
# UI
# =========================

st.set_page_config(page_title="AI Content Cloaker Ultimate", layout="centered")
st.title("🛡️ AI Content Cloaker Ultimate")
st.caption("حماية النصوص العربية/الإنجليزية والصور بشكل غير مرئي")

mode = st.radio("اختر نوع المحتوى:", ["نص", "صورة"])

# =========================
# TEXT MODE
# =========================

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
            st.success("✅ تم تحصين النص بنجاح")

# =========================
# IMAGE MODE
# =========================

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
            st.success("✅ تم تحصين الصورة بنجاح")

# Footer
st.markdown("---")
st.caption("AI Content Cloaker Ultimate | Built by Gamal Almaqtary")
