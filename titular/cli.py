import logging
import sys
from pathlib import Path
from streamlit.web import cli
from dimorphite_dl import enable_logging


def main():
    enable_logging(logging.WARNING)
    app_path = Path(__file__).parent / "app.py"
    sys.exit(cli.main(["streamlit", "run", "--log_level", "warning", str(app_path)]))


if __name__ == "__main__":
    main()