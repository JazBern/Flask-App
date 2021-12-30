from flask import Flask, render_template, request,redirect
import sqlite3 as sql
import pickle
import nltk
from nltk.corpus import stopwords
import bs4 as bs
from nltk.tokenize import sent_tokenize
import re
from nltk.stem import PorterStemmer
from nltk.tag import pos_tag
from sklearn.feature_extraction.text import CountVectorizer


app = Flask('__name__')

model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open("vector.pkl", "rb"))

@app.route('/home')
def home():
    return render_template('layout.html')

@app.route('/results',methods = ['POST', 'GET'])
def results():
    if request.method == 'POST':
        try:
            name = request.form['name']
            review = request.form['review']
            #pred = "positive"
            #1. Remove HTML tags
            updated_review = bs.BeautifulSoup(review,features="html.parser").text
            #2. Use regex to find emoticons
            emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', updated_review)
            #3. Remove punctuation
            updated_review = re.sub("[^a-zA-Z]", " ",updated_review)
            #4. Tokenize into words (all lower case)
            updated_review = updated_review.lower().split()
            #5. Remove stopwords
            eng_stopwords = set(stopwords.words("english"))
            updated_review = [w for w in updated_review if not w in eng_stopwords]
            #6. Join the review to one sentence
            updated_review = ' '.join(updated_review+emoticons)
            test_rw = [updated_review]
            tbag = vectorizer.transform(test_rw)
            prediction = model.predict(tbag)
            pred = ['Negative', 'Positive'][prediction[0]]
            with sql.connect("database.db") as con:
                cur = con.cursor()
            
                cur.execute("INSERT INTO reviews (name,review,pred) VALUES (?,?,?)",(name,review,pred) ) # ? and tuple for placeholders
            
                con.commit()
                msg = "Success"
        except:
            con.rollback()
            msg = "error in insert operation"
      
        finally:
            return render_template("results.html",msg = pred)
            con.close()

@app.route('/feedback',methods = ['POST', 'GET'])
def feedback():
    if request.method == 'POST':
        try:
            fb = request.form['feedback']
         
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("select MAX(ID) from reviews")
                res = cur.fetchone()
                max_id = res[0]
                cur.execute("UPDATE reviews SET feedback = ? WHERE ID = ?",(fb,max_id))
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"
      
        finally:
            return redirect('/home') 
            con.close()

@app.route('/list')
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("select * from reviews")
    
    rows = cur.fetchall() # returns list of dictionaries
    return render_template("list.html",rows = rows)

if __name__ == '__main__':
    app.run()
