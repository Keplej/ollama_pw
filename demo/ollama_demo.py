import ollama

model_name = 'phi'
model_detail = ollama.show(model_name)
modelfile_content = model_detail['modelfile']
# print(modelfile_content)

# generate a modelfile
# with open('mymodel.modelfile', 'w') as f:
#     f.write(modelfile_content)

with open('demo\mymodel.modelfile', 'r') as f:
    model_file = f.read()

res = ollama.create(model='jarvis_model', modelfile=model_file)
print(res)