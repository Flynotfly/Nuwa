from chat.views.chat_bot.text_answer import generate_text
from chat.providers import MODELS


ALLOWED_ANSWER_TYPES = {"text", "image", "video"}


def detect_answer_type(user_input):
    system_prompt = (
        "you will be provided with a user request. "
        "You need to determine what type of response "
        "should be given to the user. Answer in one word, "
        "don't write anything else. "
        "for example if user write 'Send me a pic' or "
        "'Generate image of something' or similar answer should be image. "
        "If user write 'generate video' it is video."
        "If user write 'Hello, how are you' then it is text."
        "Available types of responses:"
        f"{ALLOWED_ANSWER_TYPES}"
        "User prompt: "
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]
    content, info = generate_text(
        messages=messages,
        **MODELS["detect"]
    )
    content = content.strip().lower()
    print("Detect user input answer type:", repr(content))
    content = content.split(" ")[0]
    content = content.split(".")[0]
    content = content.split(",")[0]
    content = content.split("\n")[0]
    if content not in ALLOWED_ANSWER_TYPES or content == "detect":
        content = "text"
    print("Detect user input answer type:", repr(content))
    return content
