# Check wheather A Server Is Responding Correctly
import requests
a = requests.get("https://www.example.com/")


# Code to check state of connection 
def check_connection(webpage_responce):
    # true if connection succestull
    print(True if webpage_responce.status_code == 200 or 400 else False)

check_connection(a)
