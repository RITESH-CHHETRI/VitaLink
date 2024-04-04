import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import json
import numpy as np
import nltk
from nltk.stem.lancaster import LancasterStemmer
import tflearn
import tensorflow as tf
import pickle

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

class Trainer:
    def __init__(self, threshold=0.7, ignore=['?', '.', ',']):
        self.stemmer = LancasterStemmer()
        self.intents = json.loads(open('models/intents.json').read())
        self.threshold = threshold
        self.training = []
        self.output = []
        self.load_data()
        self.model = self.build_model()

    def load_data(self):
        try:
            with open("models/data.pickle", "rb") as f:
                self.words, self.labels, self.training, self.output = pickle.load(f)
        except FileNotFoundError:
            print("Error: data.pickle file not found. Please train the model first.")
            exit()

    def build_model(self):
        tf.compat.v1.reset_default_graph()
        net = tflearn.input_data(shape=[None, len(self.training[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(self.output[0]), activation="softmax")
        net = tflearn.regression(net)
        model = tflearn.DNN(net)
        model.load("models/model.tflearn")
        return model

    def bag_of_words(self, s):
        bag = [0] * len(self.words)
        s_words = nltk.word_tokenize(s)
        s_words = [self.stemmer.stem(word.lower()) for word in s_words]
        for se in s_words:
            if se in self.words:
                bag[self.words.index(se)] = 1
        return np.array(bag)

main=Trainer()

def chat(data):
    results = main.model.predict([main.bag_of_words(data)])[0]
    results_index = np.argmax(results)
    print(f"Accuracy {results[results_index]}")
    if results[results_index] > main.threshold:
        tag = main.labels[results_index]
        for t in main.intents["intents"]:
            if t["tag"] == tag:
                responses = t["responses"]
        got = responses[0]
    else:
        got = "I did not get that"
        tag = "empty"
    return tag, got

