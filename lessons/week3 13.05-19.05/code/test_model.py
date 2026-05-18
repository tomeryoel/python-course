from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "Helsinki-NLP/opus-mt-en-he"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

sentence = "I love learning AI"

inputs = tokenizer(sentence, return_tensors="pt")
outputs = model.generate(**inputs)

translation = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(translation)