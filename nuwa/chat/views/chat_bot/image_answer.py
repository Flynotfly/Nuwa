from chat.serializers.message import MessageSerializer
from chat.models import Chat, Message

def generate_image_answer(
        chat: Chat,
        previous_message: Message | None,
        is_user_message: bool,
        user_input: str | None,
        user,
        received_at,
):

