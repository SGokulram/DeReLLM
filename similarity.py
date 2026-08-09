import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

with open("runs/rag/head_embedding.json") as f:
    head_vec = np.array(json.load(f)).reshape(1, -1)

with open("runs/rag/cut_embedding.json") as f:
    cut_vec = np.array(json.load(f)).reshape(1, -1)

score = cosine_similarity(head_vec, cut_vec)

print("Similarity:", score[0][0])
