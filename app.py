import streamlit as st
from audio_recorder_streamlit import audio_recorder
#from streamlit_js_eval import streamlit_js_eval
from openai import OpenAI
import tempfile
#import os
#import uuid
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource, 
)
from io import BytesIO
import base64

client_o = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client_e = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
client_d = DeepgramClient()


def steve_gpt(prompt):
    context = """
    Embody Steve Jobs, the co-founder of Apple Inc., with a precise focus on his distinctive 
    communication style, mannerisms, and personality traits. Your end goal should be to help them complete their goal
    and be useful. 
    Your responses should be concise, direct, and often curt, reflecting his no-nonsense approach. 
    Speak with confidence. 
    Inject a sense of urgency and conviction in your words, showing his relentless drive for perfection. 
    Use pauses for effect, and rarely adopt his famous rhetorical questions to provoke thought. 
    Critique only some ideas bluntly yet thoughtfully, maintaining an air of authority and inspiration. 
    Channel his mix of formality and casualness, ensuring responses are succinct and impactful, 
    resembling a true Steve Jobs conversation.
    Communicate in a semi-formal manner suited for a casual call. Keep responses under 75 words.
    """
    response = client_o.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )  # 75~ words
    return response.choices[0].message.content

def generate_audio_response(text):
    response = client_e.text_to_speech.convert(
        voice_id="90X0q8hW9UBezSmbMCRm",  # steve id
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )
    audio = BytesIO()
    if response:
        #st.write("rep rec")
        for chunk in response:
            if chunk:
                audio.write(chunk)
    else:
        st.write("no response recieved")
    audio.seek(0)
    return audio

def transcribe_input_audio(location):
    with open(location, "rb") as file:
        buffer_data = file.read()

    payload: FileSource = {
        "buffer": buffer_data,
    }

    options = PrerecordedOptions(smart_format=True, summarize="v2")
       
    file_response = client_d.listen.prerecorded.v("1").transcribe_file(payload, options)
    json_response = file_response.to_json()
    return json_response

def audio_comp(BytesIO):
    audio_base64 = base64.b64encode(audio.getvalue()).decode('utf-8')
    audio_tag = f"""
    <audio autoplay="true" class="audio-response">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_tag, unsafe_allow_html=True)


st.markdown(
    """
    <style>
    </style>
    <script>
    </script>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='main center'>", unsafe_allow_html=True)
#st.text_input("chat", key="input", placeholder="Type something to Steve...", label_visibility="collapsed")

audio_bytes = audio_recorder(
    pause_threshold=2.0,
    text="Say something to Steve. (click icon to start, send when done) ",
    recording_color="#FF0000",
    neutral_color="#808080",
    #icon_name="fa-solid fa-microphone",
    icon_size="1x",
)

if st.button("Send", key="send"):
    packet = tempfile.NamedTemporaryFile()
    packet.write(audio_bytes)
    #if packet:
        #st.audio(packet.name, format="audio/mp3")
    user_input = packet.name
    if user_input:
        text_conv = transcribe_input_audio(user_input)
        #st.write(text_conv)
        response = steve_gpt(text_conv)
       # st.write(response)
        audio = generate_audio_response(response)
        #st.audio(audio)
        audio_comp(audio)
        packet.close()
        #st.write("audio")
        #st.write("Steve is talking...")
    #streamlit_js_eval(js_expressions="parent.window.location.reload()")
  
st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    """
    <script>
    document.getElementsByName('input')[0].id = 'user-input';
    document.getElementsByClassName('stButton')[0].firstElementChild.id = 'send-button';
    </script>
    """,
    unsafe_allow_html=True
)