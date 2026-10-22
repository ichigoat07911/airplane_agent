import json
import random

from generate_dataset import (
    make_search_sample,
    make_booking_sample,
    search_pnr_sample,
    cancel_sample
)

generator=[make_search_sample,make_booking_sample,search_pnr_sample,cancel_sample]

with open("dataset.json","w",encoding="utf-8") as f:
    for _ in range(1000):
        sample=random.choice(generator)
        each_sample=sample()
        f.write(json.dumps({"messages":each_sample})+ "\n")
print("succesfully generated 1000 samples")
