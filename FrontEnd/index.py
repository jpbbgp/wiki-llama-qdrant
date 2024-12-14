from streamlit import info as st_info
from config import MSG_HOW_TO_USE
from utils.app import run_app

def main():

    st_info(MSG_HOW_TO_USE)

if __name__ == "__main__":
    run_app(main)