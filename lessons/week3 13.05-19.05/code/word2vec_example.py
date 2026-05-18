import gensim.downloader as api

# this is a one‑time download + cache
model = api.load("glove-wiki-gigaword-50")

print("king ~ queen:", model.similarity("king", "queen"))
print("paris + germany - france →",
      [w for w,_ in model.most_similar(
          positive=["paris","germany"],
          negative=["france"],
          topn=10)])