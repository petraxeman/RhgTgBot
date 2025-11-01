import os
import random as rnd
import shutil
from contextlib import contextmanager


alphabet = list("QAZWSXEDCRFVTGBYHNUJMIKOLPqazwsxedcrfvtgbyhnujmikop1234567890")


@contextmanager
def context_temp_dir():
    temp_dir_name = gen_name()
    temp_path = os.path.join(".", "assets", "temp")
    full_path = os.path.join(temp_path, temp_dir_name)
    os.makedirs(full_path)
    yield temp_dir_name
    shutil.rmtree(full_path)


def gen_name() -> str:
    "Generate random string [A-Za-z0-9]{10}"
    name = ""
    for i in range(0, rnd.randint(10, 15)):
        name += rnd.choice(alphabet)
    return name
