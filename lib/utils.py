import time


def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)
        
    