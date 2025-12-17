from src.service import data_analysis_service


def main():
    print("Data Analysis CLI Chat")
    print("Type 'exit' to quit.\n")

    chat_history = []

    while True:
        human_message = input("You: ").strip()

        if human_message.lower() == "exit":
            print("Bye")
            break

        response = data_analysis_service(human_message, chat_history=chat_history)

        # Update chat history
        chat_history.append({"role": "user", "content": human_message})
        chat_history.append({"role": "ai", "content": str(response)})

        print(f"\nAssistant: {response}\n")


if __name__ == "__main__":
    main()
