import os
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
from sklearn.cluster import KMeans
import gensim
from gensim.models import Doc2Vec
from collections import Counter
import nltk
import json

def read_keywords(filename):
    df = pd.read_csv(filename)
    return list(df.keywords.values)

def NLTK_INIT():
    nltk.download('stopwords')
    nltk.download('wordnet')


# Function to lemmatize,clean data
def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

# use doc2vec to find vector representation then cluster
def find_clusters(keywords):
    # reading file and getting data in dataframe
    #df.drop_duplicates(['title'], keep='last')
    doc_complete = keywords

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
    kmeans_model = KMeans(n_clusters=7, init='k-means++', max_iter=100)
    X = kmeans_model.fit(d2v_model.docvecs.doctag_syn0)

    # Finding Labels
    labels=kmeans_model.labels_.tolist()

    # Finding predictions
    l = kmeans_model.fit_predict(d2v_model.docvecs.doctag_syn0)

    output = {}
    for i in labels:
        output[i]=[]

    for i in range(len(l)):
        #output[l[i]].append((df.paper_id[i], df.author_id[i], df.title[i], df.name[i],df.helsinki[i], df.keyword[i], df.year[i]))
        output[l[i]].append((keywords[i]))
    print(output)
    return output

def format_article(keywords):
    authors = pd.read_csv(os.path.join(path,"authors.csv"), encoding="iso-8859-1")
    papers = pd.read_csv(os.path.join(path,"papers.csv"))
    papersnauthors = pd.read_csv(os.path.join(path,"paper_authors.csv"))
    # join all papers
    merged = pd.merge(papers, papersnauthors, left_on="id", right_on="paper_id")
    merged = pd.merge(merged,authors,left_on='author_id',right_on='id')
    # adding binary value to papers written from helsinki authors
    merged['helsinki'] = merged['author_id'].apply(lambda x:1 if x in Helsinki_Author_ID else 0)
    merged['keyword'] = merged.title.apply(lambda x: map_title_to_keyword(x, keywords))
    return merged

def map_title_to_keyword(title, keywords):
    title = clean(title.lower()).split()
    percents = {keyword:match_words(title,keyword) for keyword in keywords}
    matched_keyword,max_percent=max(percents.items(),key=lambda x:x[1])
    if max_percent<=0: matched_keyword="Other"
    return matched_keyword

def match_words(title,keyword):
    keyword  = keyword.lower().split()
    counter_c = Counter(title+keyword)
    matched_words = [word for word in keyword if counter_c[word]>1]
    match_percent=len(matched_words)/len(keyword)*100
    return match_percent

def merge_dict(x,y):
    x.update(y)
    return x

def format_output(Keywords_Clustered,Articles):
    Output={}
    Output['name']={i:"Research Paper Topics" for i in range(len(Keywords_Clustered))}
    Output['children']=[{'name':'topic'+str(i),'children':[
        merge_dict(dict(Row[Json_Title]),{'keyword':keyword}) for keyword in Keywords_Clustered[i]  for index,Row in Articles[Articles.keyword==keyword].iterrows()
    ]} for i in range(len(Keywords_Clustered))]

    with open(os.path.join(path, Json_Name), "w") as f:
        f.write(json.dumps([Output]))
        f.close()

# declare global variable
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
Json_Title=['year','title','paper_id','author_id','name','helsinki']
Helsinki_Author_ID=[9854,1530, 9666, 9667, 9668, 5009, 7620, 7622, 7621, 9852, 9853, 9856, 2812, 9870, 4391, 1835, 5009, 8396, 8397]
Json_Name="Clustered.Json"
NLTK_INIT()
path = os.path.dirname(__file__) + '/data/'

keywords = read_keywords(os.path.join(path,"keywords14-17.txt"))
Keywords_Clustered=find_clusters(keywords)
Articles=format_article(keywords)
format_output(Keywords_Clustered,Articles)

