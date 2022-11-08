from flask import Flask, render_template, request, flash, redirect, url_for
import spacy
import sqlite3
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

nlp = spacy.load('en_core_web_sm')

con = sqlite3.connect("db.sqlite3", check_same_thread=False)
cur = con.cursor()


def summarize(text, per):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    tokens = [token.text for token in doc]
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency
    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
    select_length = int(len(sentence_tokens) * per)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = [word.text for word in summary]
    summary = ''.join(final_summary)
    return summary


def get_hotwords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN']
    doc = nlp(text.lower())
    for token in doc:
        if token.text in nlp.Defaults.stop_words or token.text in punctuation:
            continue
        if (token.pos_ in pos_tag):
            result.append(token.text)
    return result


app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/work', methods=['GET', 'POST'])
def work():
    file = request.files['file']
    typeOf = request.form['type']
    text = file.read().decode("utf-8")
    if typeOf == 'ML':
        firstAnswer = summarize(text, 0.05)
        secondAnswer = get_hotwords(text)
        first = open("first.txt", "a")
        first.write(firstAnswer)
        first.close()
        second = open("second.txt", "a")
        second.write(str(secondAnswer))
        second.close()
    if typeOf == 'Sentence_extraction':
        firstAnswer = summarize(text, 0.05)
        secondAnswer = get_hotwords(text)
        first = open("first.txt", "a")
        first.write(firstAnswer)
        first.close()
        second = open("second.txt", "a")
        second.write(str(secondAnswer))
        second.close()
    # cur.executescript("CREATE TABLE answer(firstAnswer,secondAnswer)")
    cur.execute("""INSERT INTO sqlite_master VALUES(?,?)""", (str(firstAnswer), str(secondAnswer)))
    # res = cur.execute("SELECT * FROM answer")
    # for it in res:
    #     print(it)
    con.commit()
    return render_template('index.html')


@app.route('/read', methods=['GET', 'POST'])
def read():
    first = open("first.txt", "r")
    second = open("second.txt", "r")

    return render_template('html.html', first=first.read(), second=second.read())


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    f = open('first.txt', 'r+')
    f.truncate(0)
    s = open('first.txt', 'r+')
    s.truncate(0)
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
