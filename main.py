import streamlit as st

st.set_page_config(
    page_title="Mandarin Tone Practice",
    page_icon="✨",
)

with open("style.css") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Nada Mandarin
tones = {
    1: "ā",
    2: "á",
    3: "ǎ",
    4: "à",
}


# Title and description
st.title("Latihan Berbicara Nada Mandarin")
st.write("Pilih nada yang ingin kamu pelajari")

# Display tones
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <a href='isi?selected_tone=1' style='text-decoration: none;'>
            <div class='custom-button'>
                <span class='pinyin'>{tones[1]}</span>
                <span class='tone-label'>Nada 1</span>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <a href='isi?selected_tone=3' style='text-decoration: none;'>
            <div class='custom-button'>
                <span class='pinyin'>{tones[3]}</span>
                <span class='tone-label'>Nada 3</span>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <a href='isi?selected_tone=2' style='text-decoration: none;'>
            <div class='custom-button'>
                <span class='pinyin'>{tones[2]}</span>
                <span class='tone-label'>Nada 2</span>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <a href='isi?selected_tone=4' style='text-decoration: none;'>
            <div class='custom-button'>
                <span class='pinyin'>{tones[4]}</span>
                <span class='tone-label'>Nada 4</span>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )
