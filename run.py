import argparse
import threading

from detection_engine.detector import run_detection
from messaging.consumer import start_consumer


def run_detector():
    print("Running detection engine...")
    run_detection()


def run_consumer():
    print("Starting remediation consumer...")
    start_consumer()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=["detect", "remediate", "all"],
        default="all",
        help="Mode to run the system"
    )

    args = parser.parse_args()

    if args.mode == "detect":
        run_detector()

    elif args.mode == "remediate":
        run_consumer()

    elif args.mode == "all":
        consumer_thread = threading.Thread(target=run_consumer)
        consumer_thread.start()

        run_detector()

        consumer_thread.join()
        print("Detection complete. Exiting...")

if __name__ == "__main__":
    main()