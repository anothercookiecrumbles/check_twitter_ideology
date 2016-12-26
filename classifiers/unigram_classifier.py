import csv
import numpy as np
import pickle
from scipy.sparse import csr_matrix
from sklearn import linear_model, metrics
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier

def get_score(predictions, labels):
  score = metrics.accuracy_score(labels, predictions)
  return score

def extract_features(train):
  cv = CountVectorizer(min_df=0.05, max_df=0.95,
      stop_words='english', token_pattern=r'(?u)\b\w+\b')
  train_data = cv.fit_transform(train)
  return cv, train_data

def classify_nb(data, labels, test_data, test_labels):
  data[(data > 1.0).nonzero()] = 1.0
  labels[np.where(labels <= 0)] = 0.0
  test_data[(test_data > 1.0).nonzero()] = 1.0
  test_labels[np.where(test_labels <= 0)] = 0.0

  classifier = MultinomialNB()
  classifier.fit(data, labels)
  predictions = classifier.predict(test_data)
  score = get_score(predictions, test_labels)
  print(score)
  return classifier

def classify_lasso(data, labels, test_data, test_labels):
  data[(data > 1.0).nonzero()] = 1.0
  labels[np.where(labels <= 0)] = 0.0
  test_data[(test_data > 1.0).nonzero()] = 1.0
  test_labels[np.where(test_labels <= 0)] = 0.0

  classifier = linear_model.Lasso(alpha=0.05)
  classifier.fit(data, labels)
  predictions = classifier.predict(test_data)
  print(predictions)
  error = 0
  for index, prediction in enumerate(predictions):
    if int(round(prediction)) != test_labels[index]:
      error += 1
  print(error)

  return classifier

def classify_nn(data, labels, test_data, test_labels):
  data[(data > 1.0).nonzero()] = 1.0
  labels[np.where(labels <= 0)] = 0.0
  test_data[(test_data > 1.0).nonzero()] = 1.0
  test_labels[np.where(test_labels <= 0)] = 0.0

  classifier = MLPClassifier(solver='lbfgs', alpha=1e-5,
      hidden_layer_sizes=(50,30,), random_state=1)
  classifier.fit(data, labels)
  predictions = classifier.predict(test_data)
  error = 0
  for index, prediction in enumerate(predictions):
    if int(round(prediction)) != test_labels[index]:
      error += 1
  print(error)

  return classifier

labels = list()
data = list()

test_data = list()
test_labels = list()

with open('tweets_train.csv', 'r') as csvfile:
  tweets = csv.reader(csvfile)
  for tweet in tweets:
    if tweet[0] != 'user' and tweet[1] != 'tweet':
      labels.append(tweet[2])
      data.append(tweet[1])

with open('tweets_test.csv', 'r') as csvfile:
  tweets = csv.reader(csvfile)
  for tweet in tweets:
    if tweet[0] != 'user' and tweet[1] != 'tweet':
      test_labels.append(tweet[2])
      test_data.append(tweet[1])

labels = np.array(labels, dtype=np.float64)
cv, training_data = extract_features(data)
with open('count_vectorizer.pkl', 'wb') as cvf:
  pickle.dump(cv, cvf)

training_data = csr_matrix(training_data, dtype=np.float64)

test_labels = np.array(test_labels, dtype=np.float64)
test_data = cv.transform(test_data)
test_data = csr_matrix(test_data, dtype=np.float64)

classifier = classify_lasso(training_data, labels, test_data, test_labels)
with open('classifier.pkl', 'wb') as clf:
  pickle.dump(classifier, clf)
