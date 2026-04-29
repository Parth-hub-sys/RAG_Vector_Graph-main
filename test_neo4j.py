# from retrieval.graph_retriever import graph_search
# print(graph_search("Deep Learning"))   # replace with the entity you expect

from retrieval.graph_retriever import graph_search
for q in ["machine", "learning", "machine learning", "ML"]:
    print(q, graph_search(q))
