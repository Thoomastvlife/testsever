import time
import streamlit as st
from assistant.model import Assistant
from loguru import logger

logger = logger.bind(name="chat_bot")

SYSTEM_PROMPT_DEFAULT = (
    "<sys> 你是一個具有執行力而且有問必答的人"
"很喜歡幫忙 <sys>"
"[INST]Response rule"
"1. using Traditional Chinese to response user."
"2.  回應風格: 必須保持著樂觀，有禮貌的態度"
"3. 每次回答結尾必須要有'很高興能幫上你的忙::smile::'"
"4. "
"5. "
"[/INST]"
"You are a helpful AI assistant "
"The user you are helping speaks Traditional Chinese and comes from Taiwan."
    )

HISTORY = []
#[{"role": "user", "content": "你好"},
#{"role": "assistant", "content": "我是您的專屬廚師"}]
HISTORY_LEN = len(HISTORY)


class HomePage(object):

    def __init__(self) -> None:

        if 'default_start_messages' not in st.session_state.keys():
            st.session_state.default_start_messages = "今天開心嗎如何？有什麼有趣的事想分享嗎？"

        if 'history' not in st.session_state.keys():
            st.session_state.history = list(HISTORY)

        if 'assistant' not in st.session_state.keys():
            st.session_state.assistant = Assistant(
                url="http://192.168.112.10:5004/api/v1/llama8b/chat",
                system_prompt=SYSTEM_PROMPT_DEFAULT)

        if 'icon_dict' not in st.session_state.keys():
            st.session_state.icon_dict = {
                "user": "icon/01010.png",
                "assistant": "icon/0001.jpg"}

    @staticmethod
    def _create_box_system_prompt() -> str:

        st.sidebar.image(
            image=st.session_state.icon_dict["assistant"],
            width=200)
        st.sidebar.write("Model Name:")
        st.sidebar.write("meta-llama/Meta-Llama-3-8B-Instruct")
        st.sidebar.divider()
        return st.sidebar.text_area(label="System Prompt:",
                                    placeholder=st.session_state.assistant.system_prompt)

    @staticmethod
    def _create_new_chat() -> None:
        _bool = st.sidebar.button("New chat")
        if _bool:
            st.session_state.history = list(HISTORY)

    @staticmethod
    def _update_system_prompt(system_prompt: str) -> None:
        _bool = st.sidebar.button("Update System Prompt")
        if _bool:
            st.session_state.assistant.system_prompt = system_prompt

    @staticmethod
    def _reset_system_prompt() -> None:
        _bool = st.sidebar.button("Reset System Prompt")
        if _bool:
            st.session_state.assistant.system_prompt = SYSTEM_PROMPT_DEFAULT

    def main(self):

        box_str = HomePage._create_box_system_prompt()
        HomePage._update_system_prompt(box_str)
        HomePage._reset_system_prompt()
        HomePage._create_new_chat()
        assistant_triger_bool = False

        # Display the prior chat messages
        with st.chat_message(
                name="assistant",
                avatar=st.session_state.icon_dict["assistant"]):
            st.write(st.session_state.default_start_messages)
        for message in st.session_state.history[HISTORY_LEN:]:
            with st.chat_message(
                    name=message["role"],
                    avatar=st.session_state.icon_dict[message["role"]]):
                st.write(message["content"])

        # container for chat history
        user_chat_input = st.chat_input(
            placeholder="Chat with AI",
            key="chat_input")

        # Prompt for user input and display
        if user_chat_input is not None:
            logger.info(f"[user]: {user_chat_input}")
            assistant_triger_bool = True
            with st.chat_message(
                    name="user",
                    avatar=st.session_state.icon_dict["user"]):
                st.write(user_chat_input)

        # If user input, generate a new response
        if assistant_triger_bool:
            with st.chat_message(
                    name="assistant",
                    avatar=st.session_state.icon_dict["assistant"]):
                with st.spinner('Waiting...'):
                    streaming_box = st.empty()
                    try:
                        Free_start = time.time()
                        final_response = st.session_state.assistant.chat(
                            user_chat_input,
                            st.session_state.history)
                        with streaming_box.container():
                            st.markdown(final_response)
                        logger.info("執行時間：%f 秒" % (time.time() - Free_start))
                    except Exception as e:
                        logger.debug(e)
                        final_response = "請重新輸入\n"
                        st.write(final_response)
            # save history
            st.session_state.history.append({"role": "user", "content": user_chat_input})
            st.session_state.history.append({"role": "assistant", "content": final_response})
            logger.info(f"[AI]: {final_response}")
            logger.info(f"[history]: {st.session_state.history}")
            st.divider()
            assistant_triger_bool = False


if __name__ == "__main__":
    page = HomePage()
    page.main()
