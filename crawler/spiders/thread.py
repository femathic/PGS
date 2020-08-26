import threading


def worker(work):
    t = threading.Thread(target=work)
    t.daemon = True
    t.start()
