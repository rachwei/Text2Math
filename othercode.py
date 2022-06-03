
# def get_math_parsing(text):
#   parsing = []

#   modified = get_modified_string(text)
#   modified_string = modified["modified"]
#   modified_positions = modified["positions"]
#   print("Modified string : " + modified_string)
#   doc_text = nlp(modified_string)

#   composition = {}
#   # parsing_indices = list()
#   d = {}

#   for token in doc_text:
#     if str(token) in dictionary:
#       dependencies = {}

#       recurse_cc(token, token, True, dependencies)
#       # print("composition for " + str(token))
#       # print(dependencies)
    
#       # parsing_indices.append(token.i)
#       composition[token.i] = dependencies
    
#     d[token.i] = str(token)
    
#   for token in doc_text:
#     if str(token) in dictionary:
#       ind = [i[0] for i in composition[token.i]]
#       if len(ind) > 0:
#         max_index = max(ind)
#         # parsing_indices.insert(parsing_indices.index(max_index), parsing_indices.pop(parsing_indices.index(token.i)))

#   # for ind in parsing_indices:
#   #   parsing.append(d[ind])
  
#   return parsing