
# Install on Google Colab:
# !pip install -U spacy
# !python -m spacy download en
# !python -m spacy download en_core_web_sm
# !python -m spacy download en_core_web_md

import spacy
from spacy.symbols import nsubj
from spacy import displacy
from numpy import maximum
from resources import dictionary, not_main, noun


nlp = spacy.load("en_core_web_md")

# Gets dependencies for token
def get_dependencies(token, is_root, dependencies, indices, modified_positions, nouns_found, covered_words):
  children = []
  indices.add(token.i)

  if is_root:
    children = [child for child in token.children if (child.dep_ == "dobj" or child.dep_ == "prep")]
  else:
    children = [child for child in token.children if (child.dep_ == "conj" or child.dep_ == "dobj" or child.dep_ == "prep" or child.dep_ == "pobj")]

  for dobj in children:
    if str(dobj) in dictionary:
      direct_objects = []
      get_direct_objects(dobj, direct_objects, modified_positions, covered_words)
      
      m = {}
      m[str(dobj)] = direct_objects
      dependencies.append(m)
      covered_words.append(dobj.i)

    elif dobj.pos_ == "NOUN" or dobj.pos_ == "NUM":
      nouns_found.append(dobj.i)

    get_dependencies(dobj, False, dependencies, indices, modified_positions, nouns_found, covered_words)
  
  return



# Adds direct objects of token into direct_objects
# Adds index of direct objects into covered_words
def get_direct_objects(token, direct_objects, modified_positions, covered_words):
  children = [child for child in token.children if (child.dep_ == "conj" or child.dep_ == "dobj" or 
                                                                    child.dep_ == "prep" or child.dep_ == "pobj")]
  for dobj in children:
    if str(dobj) not in dictionary:
      if dobj.pos_ == "NOUN":
        if dobj.i in modified_positions:
          direct_objects.append(str(modified_positions[dobj.i])) # Replace noun with num if it was changed during remove_num
        else:
          direct_objects.append(str(dobj))
        
        covered_words.append(dobj.i) 

      get_direct_objects(dobj, direct_objects, modified_positions, covered_words) # Recursive call on direct object
  

# Returns [closest word in dictionary, score]
def get_closest_word(word, dic):
  max_score = 0.0
  most = ""
  doc_word = nlp(word)

  for reference in dic:
    doc_reference = nlp(reference)
    score = doc_word.similarity(doc_reference)

    if (score > max_score):
      max_score = score
      most = reference

  doc_most = nlp(most)
  print(doc_word, "<->", doc_most, max_score)

  returnvalue = dict()
  returnvalue['closest_word'] = most
  returnvalue['score']  = max_score
  return returnvalue



# Replaces words with their lemmas if it is in the dictionary (eg. "Subtracted" -> "subtract")
def replace_lemmas(text):
  doc_text = nlp(text.lower())
  modified = ""

  for token in doc_text: 
    if token.lemma_ in dictionary:
      modified += str(token.lemma_) + " "
    else:
      modified += str(token) + " "
  
  return modified


# Handles the takes the ___ etc. situations 
# (eg. "take the product of __ and the sum of __ and add them" -> "add the product of _ and the sum of _")
def preprocess(text):
  index = -1
  word_to_swap = ""
  root = ""
  doc_text = nlp(text)

  for token in doc_text:
    if token.dep_ == "ROOT":
      root = str(token)

      if str(token) in not_main:
        children = [word for word in token.children if (word.dep_ == "conj")]
        if len(children) > 0:
          new_root = children[0]
          index = new_root.i
          word_to_swap = str(new_root)
      break

  if index != -1 and word_to_swap not in not_main:
    # swap the root with the verb and trim accordingly
    array = text.split(" ")
    array[array.index(root)] = word_to_swap
    array = array[:index - 1] + array[index + 2:]
    text = " ".join(array)

  return text


# Replaces numbers with specified noun from resources
# Returns [modified string, indicies of previous numbers]
def replace_numbers(text):
  doc_text = nlp(text)
  modified_string = ""
  modified_positions = {}

  for token in doc_text:
    if token.like_num and len(str(token)) == 1:
      modified_string += noun + " "
      modified_positions[token.i] = str(token)
    else:
      modified_string += str(token) + " "

  returnvalue = dict()
  returnvalue['modified_string'] = modified_string
  returnvalue['modified_positions']  = modified_positions
  return returnvalue




#gets parsing of text
def get_math_parsing(text):
  
  modified_string = replace_lemmas(text)
  modified_string = preprocess(modified_string) 

  modified = replace_numbers(modified_string)
  modified_string = modified["modified_string"]
  modified_positions = modified["modified_positions"]

  doc_text = nlp(modified_string)
  # displacy.render(doc_text, style="dep", jupyter=True) # Uncomment on Google Colab to show graph

  result = []
  indices_explored = set() # Keeps track of the words explored
  
  for token in doc_text:
    if str(token) in dictionary and token.i not in indices_explored:
      dependencies = []
      other_nouns = []
      covered_words = []

      get_dependencies(token, True, dependencies, indices_explored, modified_positions, other_nouns, covered_words)

      if len(dependencies) != 0:
        result.append(dependencies)

      m = {}
      final = []

      for i in range(len(other_nouns)):
        if other_nouns[i] not in covered:
          if other_nouns[i] in modified_positions:
            final.append(str(modified_positions[other_nouns[i]]))
          else:
            final.append(str(doc_text[other_nouns[i]]))
      m[str(token)] = final
      result.append([m])
  
  return result



if __name__ == "__main__":
  import sys

  #default sentence
  test_string = "Subtract the product of 3 and 4 from the sum of 5 and 6 and 7"

  if len(sys.argv) > 1:
    test_string = sys.argv[1]

  print(test_string + " parsed is: ")
  math_parsing = get_math_parsing(test_string)
  print(math_parsing)



#Testing
def test_cases():
  test_string = "Subtract the product of 3 and 4 from the sum of 5 and 6"
  assert get_math_parsing(test_string) == [[{'product': ['3', '4']}, {'sum': ['5', '6']}], [{'subtract': []}]]

  test_string = "Take the product of 3 and 4 and the sum of 5 and 6 and add them"
  assert get_math_parsing(test_string) == [[{'product': ['3', '4']}, {'sum': ['5', '6']}], [{'add': []}]]

  test_string = "Add the product of 3 and 4 and the product of 5 and 6"
  assert get_math_parsing(test_string) == [[{'product': ['3', '4']}, {'product': ['5', '6']}], [{'add': []}]]

  test_string = "Subtract the first digit by the second digit and then multiply it by 3"
  assert get_math_parsing(test_string) == [[{'subtract': ['digit', 'digit']}], [{'multiply': ['3']}]]

  test_string = "Subtract the first one by the second one and then multiply it by 3 and then add 5"
  assert get_math_parsing(test_string) == [[{'subtract': ['one', 'one']}], [{'multiply': ['3']}], [{'add': ['5']}]]

  test_string = "Set x to the sum of 3 and 4 and then multiply it by the sum of 5 and 6"
  assert get_math_parsing(test_string) == [[{'sum': ['3', '4']}, {'sum': ['5', '6']}], [{'multiply': []}]]

  test_string = "Take the product of 3 and 4 and the sum of 5 and 6 and add them and then subtract it from the sum of 6 and 8"
  assert get_math_parsing(test_string) == [[{'product': ['3', '4']}, {'sum': ['5', '6']}], [{'add': []}], [{'sum': ['6', '8']}], [{'subtract': []}]]

  # test_string =  "Divide 3 by 4 and then add the product of that and 5 and the product of 5 and 6"
  # assert get_math_parsing(test_string) == [["divide"], ["product", "product"], ["add"]]

  # test_string = "Divide x by y and then take the answer and divide it by the sum of 7 and 8 and the product of 5 and 7"
  # assert get_math_parsing(test_string) == [["divide"], ["sum", "product"], ["divide"]]
  # "divide" -> ("divide", "5", "6")
  # divide("5", "6") -- make a class?
  # &1 = sum("3", "4")
  # &2 = sum("4", "5")
  # multiply("&1", "&2")


  #Instances where it doesn't work
  # test_string = "Set x to the sum of 3 and 4 after multiplying it by the product of 5 and 6" #do a special case with after?
  # assert get_math_parsing(test_string) == [["muliply", "product"], ["sum"]]

  # test_string =  "Find the sum of 3 by 4 and then take that answer and divide that by the sum of the first and second column"
  # assert get_math_parsing(test_string) == [["sum"], ["sum"], ["divide"]] #limitation in parsing


# """Pytest test"""

# def test_answer():
#   assert inc(3) == 5
#   assert 4 == 5
#   where 4 = inc(3)





#pull out operators
# def update_operators(dict, text):
#   #replace every word with the words and if the dependencies dont change then add it to the dictionary
#   #go through dictionary and find something with the same department
#   to_replace = ""

#   doc_text = nlp(text)

#   for token in doc_text:
#     word_type = token.pos_
#     position = token.i

#     if str(token) not in dictionary and str(token) not in not_main and (word_type == "NOUN" or word_type == "VERB"):
#       for word in dictionary:
#         dict_text = nlp(text)

#         sentence1 = text
#         array = str(sentence1).split(" ")
#         array[position] = word
#         sentence2 = " ".join(array)

#         # print(sentence1)
#         # print(sentence2)
        
#         if (dict_text[0].dep_ == word_type and are_dependencies_same(sentence1, sentence2)):
#           print("word that could be important: " + str(token))



# def are_dependencies_same(text, text1):
#   doc_text = nlp(text)
#   doc_text2 = nlp(text1)

#   if (len(doc_text) != len(doc_text2)):
#     return False
  
#   for i in range(len(doc_text)):
#     word1 = doc_text[i]
#     word2 = doc_text2[i]
#     if word1.pos_ != word2.pos_ or word1.dep_ != word2.dep_ or word1.head.text != word2.head.text:
#       return False
  
#   return True