import requests
import streamlit as st
import replicate

st.set_page_config(layout="wide")

st.title("Design advisor")
st.subheader("get feedback here before showing your work to a jury 🫢")

# Define a hardcoded system prompt
SYSTEM_PROMPT = "You are an art teacher, guiding young artists to improve their designs. Provide concise critiques, highlighting 3 areas for improvement, with reasons why. Offer actionable advice to enhance their artistic expression. Keep responses short, focused, and easy to understand."

def upload_image_to_fileio(image_file):
    files = {'file': image_file}
    response = requests.post('https://file.io', files=files)
    response_data = response.json()
    if response.status_code == 200 and response_data['success']:
        return response_data['link']
    else:
        raise Exception("Failed to upload image to file.io")

def upload_image():
    images = st.file_uploader("Upload an image to chat about", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    # assert max number of images, e.g. 7
    assert len(images) <= 7, (st.error("Please upload at most 7 images"), st.stop())

    if images:
        # display images in multiple columns
        cols = st.columns(len(images))
        for i, col in enumerate(cols):
            col.image(images[i], caption=f"Image {i+1}")
        st.markdown("---")
        return images
    st.stop()

@st.cache_data(show_spinner=False)
def ask_replicate(question, image_files):
    responses = []
    for image_file in image_files:
        image_url = upload_image_to_fileio(image_file)
        
        input = {
            "image": image_url,
            "prompt": f"{SYSTEM_PROMPT}\n{question}"
        }

        output = replicate.run(
            "yorickvp/llava-13b:b5f6212d032508382d61ff00469ddda3e32fd8a0e75dc39d8a4191bb742157fb",
            input=input
        )
        responses.append("".join(output))
    return responses

def app():
    st.markdown("---")
    # c1, c2 = st.columns(2)
    # with c2:
    image_files = upload_image()
    # with c1:
    question = st.chat_input("Ask a question about the image(s)")
    if not question: st.stop()
    # with c1:
    with st.chat_message("question"):
        st.markdown(question, unsafe_allow_html=True)
    with st.spinner("Thinking..."):
        responses = ask_replicate(question, image_files)
        for response in responses:
            with st.chat_message("response"):
                st.write(response)

if __name__ == "__main__":
    app()
