import os
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
from pprint import pprint
from sklearn.cluster import KMeans
import gensim
from gensim.models import Doc2Vec
from collections import Counter


# To get path and pandas display option
path = os.path.dirname(__file__) + '/data/'
pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 200)


stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

# Function to lemmatize,clean data
def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

# use doc2vec to find vector representation then cluster
def find_clusters(df):
    # reading file and getting data in dataframe
    df.drop_duplicates(['title'], keep='last')
    doc_complete = df.title.values

    # clean the documents
    doc_clean = [clean(doc) for doc in doc_complete]

    # Importing Gensim
    LabeledSentence1 = gensim.models.doc2vec.TaggedDocument

    # Making Labeled Sentences for Doc2Vec
    all_content = [LabeledSentence1(doc,[i]) for i, doc in enumerate(doc_clean)]

    # Calling Doc2Vec Model
    d2v_model = Doc2Vec()

    # Calling Function to Build on the Go Vocabulary
    d2v_model.build_vocab(all_content)

    # Calling Function to train the model
    d2v_model.train(all_content, total_examples=d2v_model.corpus_count, epochs=10, start_alpha=0.002, end_alpha=-0.016)

    # Applying Kmeans Clustering Algorithm, n_cluster can be tweaked
    kmeans_model = KMeans(n_clusters=4, init='k-means++', max_iter=100)
    X = kmeans_model.fit(d2v_model.docvecs.doctag_syn0)

    # Finding Labels
    labels=kmeans_model.labels_.tolist()

    # Finding predictions
    l = kmeans_model.fit_predict(d2v_model.docvecs.doctag_syn0)

    output = {}
    for i in labels:
        output[i]=[]

    for i in range(len(l)):
        output[l[i]].append((df.paper_id[i], df.author_id[i], df.title[i], df.name[i],df.helsinki[i], df.keyword[i], df.year[i]))

    return output

# read files in and format
def format_data(keywords):
    authors = pd.read_csv(os.path.join(path,"authors.csv"), encoding="iso-8859-1")
    papers = pd.read_csv(os.path.join(path,"papers.csv"))
    papersnauthors = pd.read_csv(os.path.join(path,"paper_authors.csv"))
    merged = pd.merge(papers, papersnauthors, left_on="id", right_on="paper_id")
    merged2 = pd.merge(merged,authors,left_on='author_id',right_on='id')
    merged2['helsinki'] = 0
    merged2["keyword"]="Other"

    # adding binary value to papers written from helsinki authors
    c = merged2[merged2['paper_text'].str.contains("Helsinki")].id_x.tolist()
    merged2.helsinki[c]=1
    merged2['keyword']=merged2.title.apply(lambda x : map_title_to_keyword(x, keywords))
    return merged2

# mapping for keywords
def map_title_to_keyword(title, keywords):
    title = clean(title.lower()).split()
    percents = []
    for keyword in keywords:
        match_percent = match_words(title, keyword)
        percents.append(match_percent)
    max_percent = max(percents)
    matched_keyword = "Other"
    if max_percent>0:
        max_indx = percents.index(max_percent)
        matched_keyword = keywords[max_indx]

    return matched_keyword

def read_keywords(filename):
    df = pd.read_csv(filename)
    return list(df.keywords.values)

def match_words(title,keyword):
    keyword  = keyword.lower().split()
    combined = title+keyword
    counter_c = Counter(combined)
    matched_words = []

    for word in keyword:
        if counter_c[word]>1:
            matched_words.append(word)
    if matched_words:
        match_percent = len(matched_words)/len(keyword)*100
    else:
        match_percent = 0
    return match_percent

def output_formatter(input_dict,output_file):
    output_dict = {}
    output_dict["name"]="Research Paper Topics"
    output_dict["children"]=[]
    for key in input_dict.keys():
        ids = list(input_dict[key])
        outkey = "topic-"+str(key)
        out ={}
        out["name"]=outkey
        out["children"]=[]

        for tup in ids:
            outn = {}
            outn['paper_id']=tup[0]
            outn['author_id']=tup[1]
            outn['title']=tup[2]
            outn['author']=tup[3]
            outn['name']=tup[3]
            outn['helsinki']=tup[4]
            outn['keyword']=tup[5]
            outn['year']=tup[6]
            out["children"].append(outn)
        output_dict["children"].append(out)

    pprint(output_dict)
    final_out = pd.DataFrame(output_dict)
    #final_out = final_out[final_out['keyword']=='Other'] # exclude other
    final_out.to_json(output_file)

if __name__ == '__main__':
    output_file = "clusters.json"
    keywords = read_keywords(os.path.join(path,"keywords14-17.txt"))
    df = format_data(keywords)
    output_data = find_clusters(df)
    output_formatter(output_data,output_file)
