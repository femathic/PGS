import yake
import json


with open('./bucket/data.json') as json_file: 
    data = json.load(json_file) 



def keyword_extractor(text):
  keywords_list = []
  custom_kw_extractor = yake.KeywordExtractor(lan='en', n=3, dedupLim=0.9, dedupFunc='segm', windowsSize=1, top=80, features=None)
  keywords = custom_kw_extractor.extract_keywords(text)
  for keyword, percentage in keywords:
    keywords_list.append(keyword)
  return keywords_list



def fetchData(keyword, school):
  keywords_list = keyword_extractor(keyword)
  stopwords = ['professor', 'lecturer', "study", 'course', 'faculty', 'department']
  keywords_list = [word for word in keywords_list if word not in stopwords]
  print(school, keyword)
  print(keywords_list)

  filteredData = []
  if (school != 'all'):
    for value in data:
      if school in value['url']:
        filteredData.append(value)
  else:
    filteredData = list(data)

  newData = []
  for value in filteredData:
    rating = 0
    for word in keywords_list:
      if (word in value['bio'].lower().split()):
        rating += 30
      if (word in value['name'].lower().split()):
        rating += 50
      if (word in [x.lower() for x in value['expertise']]):
        rating += 2
      if (word in  value['department']):
        rating += 2
    if rating > 0:
      value['rating'] = rating
      newData.append(value)
  return sorted(newData, key=lambda k: k['rating'], reverse=True)
