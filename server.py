from flask import Flask, render_template, request
import time
from fetchData import fetchData
  
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        start = time.time()
        keyword = request.form.get('keyword')
        school = request.form.get('school')
        if (len(keyword) < 3 or not school):
            return render_template('home.html', data=[], noResults=True)
        result =fetchData(keyword, school)
        noResults = True if len(result) == 0 else False
        end = time.time()
        return render_template('home.html', data=result, time=end-start, dataLength=len(result), noResults=noResults, keyword=keyword, school=school)
    return render_template('home.html', data=[])

@app.errorhandler(404) 
def not_found(e): 
  return render_template("404.html") 

if __name__ == "__main__":
    app.run(debug=True)