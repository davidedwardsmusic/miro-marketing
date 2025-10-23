import os
from typing import Optional
from dotenv import load_dotenv

from src.backend.poller import BoardPoller


def main() -> None:

    # Access token is validated inside MiroApiClient on first use
    poller = BoardPoller()
    try:
        poller.run_forever()
    except KeyboardInterrupt:
        print("[main] Stopped by user")


if __name__ == "__main__":
    main()

