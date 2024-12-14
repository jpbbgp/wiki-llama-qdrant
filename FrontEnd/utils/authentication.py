import streamlit as st
import yaml
import time

# Read user data from the YAML file


def read_user_data():
    try:
        with open("users.yaml", "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {}

# Write user data to the YAML file


def write_user_data(data):
    with open("users.yaml", "w") as file:
        yaml.dump(data, file)


def login():
    pass    