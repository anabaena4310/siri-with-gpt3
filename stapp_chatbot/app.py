import streamlit as st
import pya3rt

apikey = "DZZbHdU8i6DyNufqdG2UIvoHH0qtCewG"
client = pya3rt.TalkClient(apikey)

chat_logs = []

st.title("Chatbot with streamlit")

st.subheader("メッセージを入力してから送信をタップしてください")

message = st.text_input("メッセージ")

def send_pya3rt():
    ans_json = client.talk(message)
    ans = ans_json['results'][0]['reply']
    chat_logs.append('you: ' + message)
    chat_logs.append('AI: ' + ans)
    for chat_log in chat_logs:
        st.write(chat_log)

if st.button("送信"):
    send_pya3rt
