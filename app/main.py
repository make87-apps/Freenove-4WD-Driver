import time

from make87_messages.text.text_plain_pb2 import PlainText
from make87 import initialize, get_publisher, resolve_topic_name


def main():
    initialize()
    topic_name = resolve_topic_name("HELLO_WORLD_MESSAGE")
    topic = get_publisher(name=topic_name, message_type=PlainText)

    while True:
        message = PlainText(body="Hello, World! 🐍")
        topic.publish(message)
        print(f"Published: {message}")
        time.sleep(1)


if __name__ == "__main__":
    main()
