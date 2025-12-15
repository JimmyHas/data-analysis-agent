import argparse

from src.service import data_analysis_service

def render_response(response) -> str:
    """
    Make the CLI output nice even if response is an object.
    Adjust this based on what your generators return.
    """
    if response is None:
        return "No response."

    if isinstance(response, str):
        return response

    for key in ("text", "content", "message", "sql", "answer", "output"):
        if hasattr(response, key):
            val = getattr(response, key)
            if isinstance(val, str) and val.strip():
                return val
        if isinstance(response, dict) and key in response and isinstance(response[key], str):
            if response[key].strip():
                return response[key]

    return str(response)


def chat_loop():
    print("Data Analysis CLI Chat")
    print("Type 'exit' to quit.\n")

    chat_history = []
    while True:
        try:
            human_message = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            return

        if not human_message:
            continue

        if human_message.lower() in {"exit", "quit", "q", ":q"}:
            print("Bye!")
            return

        chat_history.append({"role": "user", "content": human_message})

        try:
            response = data_analysis_service(human_message, chat_history)
        except Exception as e:
            print(f"[error] {e}")
            continue

        printable = render_response(response)
        chat_history.append({"role": "assistant", "content": printable})

        print(printable)


def main(argv=None):
    parser = argparse.ArgumentParser(description="CLI chat for data_analysis_service")
    parser.add_argument(
        "--once",
        type=str,
        default=None,
        help="Run a single prompt and exit (useful for scripts).",
    )
    args = parser.parse_args(argv)

    if args.once is not None:
        chat_history = [{"role": "user", "content": args.once}]
        response = data_analysis_service(args.once, chat_history)
        printable = render_response(response)
        chat_history.append({"role": "assistant", "content": printable})
        print(printable)
        return 0

    chat_loop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
