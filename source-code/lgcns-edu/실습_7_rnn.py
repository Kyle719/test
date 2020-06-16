# -*- coding: utf-8 -*-
"""실습_7_RNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Kq2lkngLvgw2VGsxzozpRKGVFQs5bUz5

# 감성분석 실습

<b>학습 목표:    
- 한국어 자연어처리의 전반적인 FLOW를 이해한다.
- keras.Sequantial 모듈을 이용해 간단한 감성분석 모델을 구현해 학습하고, 학습 결과를 진단한다.</b>

<font color = "red"> 
QUIZ:   
숫자만 인식할 수 있는 기계학습 모델에게 자연어를 인식시키는 방법은? </font>
"""

# Commented out IPython magic to ensure Python compatibility.
try: 
#   %tensorflow_version 2.x
except Exception:
  pass

import numpy as np

import tensorflow as tf

from tensorflow.keras import Model

from tensorflow.keras import layers
import tensorflow_datasets as tfds
tfds.disable_progress_bar()

""" 한국어 형태소 분석 라이브러리 """
!pip install konlpy

"""# # 1. 자연어처리 플로우 이해하기

### Step 1. Parsing
- konply : 한국어 자연어처리 관련 패키지
- konply의 Okt tagger을 이용해 형태소 분석 실행

<img src = "https://github.com/seungyounglim/temporary/blob/master/image_2.PNG?raw=true">
"""

from konlpy.tag import Okt
okt=Okt()

def tokenize(lines): 
  return [pos[0] for pos in okt.pos(lines)]

sentence1 = "시간 가는 줄 알고 봤습니다."
sentence2 = "안보면 후회ㅠㅠ..."
parsed_sent1 = tokenize(sentence1)
parsed_sent2 = tokenize(sentence2)
print("문장 1:", parsed_sent1)
print("문장 2:", parsed_sent2)

"""### Step 2. 모델 인풋 만들기

<img src = "https://github.com/seungyounglim/temporary/blob/master/image_3.PNG?raw=true">

#### 2-1) 단어 사전 만들기
자연어 형태소를 모델이 처리할 수 있는 정수 인덱스로 변환해야 함
- 형태소 분석된 단어를 정수로 매핑하는 사전 만들기
- 배치 연산을 위해 필요한 Padding([PAD])과 Out of vocabulary([OOV]) 토큰을 항상 맨 앞에 추가해둠
"""

vocab_dict = {}
vocab_dict["[PAD]"] = 0
vocab_dict["[OOV]"] = 1
i = 2
for word in parsed_sent1:
    if word not in vocab_dict.keys():
        vocab_dict[word] = i
        i += 1
for word in parsed_sent2:
    if word not in vocab_dict.keys():
        vocab_dict[word] = i
        i += 1
print("Vocab Dictionary Example:")
print(vocab_dict)

"""#### 2-2) vocab_dict를 이용해 자연어를 정수 인덱스로 바꾸기
- 위에서 만든 vocab_dict를 이용해 파싱해둔 문장을 모델에 태울 수 있는 정수 인덱스로 바꾸기
- 기본적으로 LSTM은 가변적인 문장 길이를 인풋으로 받을 수 있지만, 배치 처리를 위해 <font color="blue">max_seq_len</font>을 정해두고 길이를 통일함    
    - max_seq_len 보다 짧은 문장에는 max_seq_len이 될 때까지 [PAD]에 해당하는 인덱스를 붙여줌
    - max_seq_len 보다 긴 문장은 max_seq_len 개의 토큰만 남기고 자름   
       - 앞에서부터 max_seq_len 만큼의 토큰만 사용한다거나
       - 뒤에서부터 max_seq_len 만큼의 토큰만 사용하거나
       - 중간부분에서 max_seq_len 만큼만 사용함
    - tensorflow.keras.preprocessing.sequence의 <font color="blue">pad_sequences</font> 사용
"""

max_seq_len = 10

input_id1 = [vocab_dict[word] for word in parsed_sent1]
input_id2 = [vocab_dict[word] for word in parsed_sent2]

# Padding
from tensorflow.keras.preprocessing.sequence import pad_sequences
input_ids = [input_id1, input_id2]
input_ids = pad_sequences(input_ids, maxlen=max_seq_len, value = vocab_dict['[PAD]']) 
print(input_ids)

"""### Step3. 모델 만들기

<img src = "https://github.com/seungyounglim/temporary/blob/master/image_4.PNG?raw=true">

- <b>tf.keras.Sequential()</b> 을 사용해 모델 구현하기
- Sequential()은 레이어를 연속적으로 쌓아서 모델로 만들 수 있음
    - 임베딩 레이어 : layers.Embedding()
    - LSTM : layers.LSTM()
    - FC layer : layers.Dense()   
- LSTM을 사용해 문장을 인코딩하고, Fully Connected layer을 두 층 쌓아 최종 output을 생성
"""

vocab_size = len(vocab_dict) # 단어사전 개수
embedding_dim = 30 # 임베딩 차원
lstm_hidden_dim = 50 # LSTM hidden_size 
dense_dim = 50 #FC layer size
batch_size = 2 # batch size

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim),
    tf.keras.layers.LSTM(lstm_hidden_dim),
    tf.keras.layers.Dense(dense_dim, activation='relu'),
    tf.keras.layers.Dense(2, activation='softmax')
])

"""- <b>model.summary()</b> : 모델 구조, 파라메터 개수를 한 눈에 보여줌"""

model.summary()

"""- <b>tf.keras.utils.plot_model()</b> : 인풋 ~ 아웃풋까지 텐서의 흐름을 그림으로 나타냄"""

tf.keras.utils.plot_model(model, "LSTM_sentiment_analysis.png", show_shapes = True)

"""- <b>model.predict()</b> 메서드를 사용하면 인풋에 대해 모델의 예측값을 얻을 수 있음."""

scores = model.predict(input_ids)

for i, s in enumerate(scores):
    print("문장 {} → 긍정: {:.2f} / 부정: {:.2f}".format(i, s[0],s[1]))

"""# # 2. LSTM으로 감성분석 모델 훈련하기

### Step 0. 학습 데이터 준비하기
<img src = "https://github.com/seungyounglim/temporary/blob/master/image_5.PNG?raw=true">    

- 네이버 영화 감성분석 데이터셋 활용
- 훈련 데이터 150,000건, 테스트 데이터 50,000건
"""

""" 네이버 영화 리뷰 데이터셋 다운로드 """
!wget https://raw.githubusercontent.com/e9t/nsmc/master/ratings_train.txt
!wget https://raw.githubusercontent.com/e9t/nsmc/master/ratings_test.txt

""" 데이터 읽어오기 """

with open("ratings_train.txt") as f:
    raw_train = f.readlines()
with open("ratings_test.txt") as f:
    raw_test = f.readlines()
raw_train = [t.split('\t') for t in raw_train[1:]]
raw_test = [t.split('\t') for t in raw_test[1:]]

FULL_TRAIN = []
for line in raw_train:
    FULL_TRAIN.append([line[0], line[1], int(line[2].strip())])
FULL_TEST = []
for line in raw_test:
    FULL_TEST.append([line[0], line[1], int(line[2].strip())])
print("FULL_TRAIN: {}개 (긍정 {}, 부정 {})".format(len(FULL_TRAIN), sum([t[2] for t in FULL_TRAIN]), len(FULL_TRAIN)-sum([t[2] for t in FULL_TRAIN])), FULL_TRAIN[0])
print("FULL_TEST : {}개 (긍정 {}, 부정 {})".format(len(FULL_TEST), sum([t[2] for t in FULL_TEST]), len(FULL_TEST)-sum([t[2] for t in FULL_TEST])), FULL_TEST[0])

"""### label 
> 0: 부정

> 1: 긍정
"""

# 데이터 예시 : id, 문장, 라벨 순서
print(FULL_TRAIN[0])

"""<img src = "https://github.com/seungyounglim/temporary/blob/master/image_6.PNG?raw=true">  
- 시간 관계상 train 중 50,000건을 학습데이터, 10,000건을 검증 데이터로 사용
- test 중 10,000건만 샘플링하여 최종 성능 테스트에 사용
"""

import random
random.seed(1)
random.shuffle(FULL_TRAIN)
random.shuffle(FULL_TEST)
train = FULL_TRAIN[:50000]
val = FULL_TRAIN[50000:60000]
test = FULL_TEST[:10000]
print("train     : {}개 (긍정 {}, 부정 {})".format(len(train), sum([t[2] for t in train]), len(train)-sum([t[2] for t in train])), train[0])
print("validation: {}개 (긍정 {}, 부정 {})".format(len(val), sum([t[2] for t in val]), len(val)-sum([t[2] for t in val])), val[0])
print("test      : {}개 (긍정 {}, 부정 {})".format(len(test), sum([t[2] for t in test]), len(test)-sum([t[2] for t in test])), test[0])

"""## Step 1. Parsing
- Train/ Test의 문장을 형태소분석기로 파싱하여 train_sentences, test_sentences에 저장해둠.
- categorical_crossentropy loss를 사용하기 위해 정답 라벨은 One-hot encoding 형식으로 저장
   - 부정 -> [1, 0]
   - 긍정 -> [0 , 1]
"""

train_sentences = []
val_sentences = []
test_sentences = []

# 추후 학습/ 테스트를 위해 라벨 정보 저장해둠
train_label_ids = []
val_label_ids = []
test_label_ids = []

print("start tokenizing TRAIN sentences")
for i, line in enumerate(train):
    tokens = tokenize(line[1])
    train_sentences.append(tokens)
    if line[2] == 0: # 부정
      train_label_ids.append([1,0])
    else: #긍정
      train_label_ids.append([0,1])

    if (i+1) % 5000 == 0: print("... {}/{} done".format(i+1, len(train)))

print("example:", train_sentences[-1], train_label_ids[-1], "\n")

print("start tokenizing VALIDATION sentences")

for line in val:
    tokens = tokenize(line[1])
    val_sentences.append(tokens)
    if line[2] == 0: # 부정
      val_label_ids.append([1,0])
    else: #긍정
      val_label_ids.append([0,1])
print("... done\n")

print("start tokenizing TEST sentences")
for line in test:
    tokens = tokenize(line[1])
    test_sentences.append(tokens)
    if line[2] == 0: # 부정
      test_label_ids.append([1,0])
    else: #긍정
      test_label_ids.append([0,1])

print("... done")

"""##Step 2. 모델 인풋 만들기

#### 2-1) 단어사전 만들기
- 훈련 데이터 문장에 있는 형태소를 이용해 구축
- (일반적으로는 더 많은 코퍼스에 대해 구축된 사전을 사용하지만, 편의상 훈련셋만으로 진행)

# 실습 MISSION #14
[CODE] 부분을 채워넣어 단어사전을 만들고 생성된 단어사전의 크기를 확인해보세요.
"""

from tqdm import tqdm

vocab_dict = {}
vocab_dict["[PAD]"] = 0
vocab_dict["[OOV]"] = 1
i = 2
for sentence in train_sentences:
    for word in sentence:
        if word not in vocab_dict.keys():
            ## [CODE] ##
            vocab_dict[word] = i
            ############
            i += 1
print("Vocab Dictionary Size:", len(vocab_dict))

"""#### 2-2) vocab_dict를 이용해 자연어를 정수 인덱스로 바꾸기

# 실습 MISSION #15
> 토큰화된 문장들 (tokenized_sentences)을 인풋으로 받아 다음을 처리하는 함수를 만드시오

* 단어사전에 없는 단어는 [OOV] 인덱스로 처리하기   
* 단어사전에서 매핑되는 단어는 해당 인덱스로 바꾸기   
* 문장 길이를 'max_seq_len'으로 맞추어, max_seq_len보다 긴 문장은 뒷부분을 자르고, max_seq_len보다 짧은 문장은 뒷부분에 padding하기
"""

def make_input_ids(tokenized_sentences, max_seq_len = 50):
  
  num_oov = 0 # OOV 발생 개수를 셈
  result_input_ids = [] # result_input_ids : 정수 인덱스로 변환한 문장들의 리스트

  for sentence in tokenized_sentences :
      """ vocab_dict를 사용해 정수로 변환 """ 
      input_ids = []
      for token in sentence:
          if token not in vocab_dict: 
              input_ids.append(vocab_dict['[OOV]']) ## a. [CODE] OOV 처리
              num_oov += 1
          else:
              input_ids.append(vocab_dict[token]) ## b. [CODE] 단어사전에서 토큰 찾아서 붙이기
      
      result_input_ids.append(input_ids)
      
  """ max_seq_len을 넘는 문장은 절단, 모자르는 것은 PADDING """
  result_input_ids = pad_sequences(result_input_ids, maxlen=max_seq_len, padding='post', truncating='post', value = 0) ## c. [CODE] padding 하기

  return result_input_ids, num_oov

# train_sentences 처리
train_input_ids, num_oov = make_input_ids(train_sentences)

print("---- TRAIN ----")
print("... # OOVs     :", num_oov)

# val_sentences 처리
val_input_ids, num_oov = make_input_ids(val_sentences)

print("---- VALIDATION ----")
print("... # OOVs     :", num_oov)

# test_sentences 처리
test_input_ids, num_oov = make_input_ids(test_sentences)

print("---- TEST ----")
print("... # OOVs     :", num_oov)

"""#### 2-3) 라벨 리스트를 np.array로 변환
- TIP: tensorflow2.0에서는 numpy array를 인풋으로 받아들임
"""

train_label_ids = np.array(train_label_ids)
val_label_ids = np.array(val_label_ids)
test_label_ids = np.array(test_label_ids)

"""## Step3. 모델 만들기

# 실습 MISSION #16
> 아래 조건에 맞는 모델을 만드시오
 
* embedding 차원은 150
* LSTM hidden size는 100
* Dense의 hidden size는 100, relu activation 사용
* output Dense layer에서는 긍/부정 2개 카테고리를 분류하되 softmax 사용
"""

tf.keras.backend.clear_session()

from tensorflow.keras.layers import Embedding, LSTM, Dense

vocab_size = len(vocab_dict) 

model = tf.keras.Sequential([
            ####### MISSION 작성 ######
            tf.keras.layers.Embedding(vocab_size, 150),
            tf.keras.layers.Dropout(rate = 0.2),
            tf.keras.layers.LSTM(100),
            tf.keras.layers.Dropout(rate = 0.2),
            tf.keras.layers.Dense(100, activation='relu'),
            tf.keras.layers.Dense(2, activation='softmax')
            ###########################
])

model.summary()

"""## Step 4. 모델 훈련하기

#### 4-1) <b>model.compile()</b>을 통해 loss, optimizer 지정
"""

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

"""#### 4-2) model.fit()을 통해 모델 훈련"""

num_epochs = 5
history = model.fit(train_input_ids, train_label_ids, epochs=num_epochs, validation_data=(val_input_ids, val_label_ids), verbose=2) 

test_result = model.evaluate(test_input_ids, test_label_ids, verbose=2)

"""<font color='purple'>🚴‍♀️<i> while training...</i></font>   
<br>
<u> keras RNN API 확인하기</u>
- https://www.tensorflow.org/guide/keras/rnn
- 기본적인 RNN 이외에 Bidirectional RNN, Multi-layer RNN 구조 등을 활용하고 싶다면 API 문서를 참고해 만들 수 있음.
- 예) 
  - LSTM의 모든 timestep의 output을 받아오려면 
  - lstm = tf.keras.layers.LSTM(hidden_dim, return_sequences=True)로 설정
  - Bidirectional-LSTM을 사용하려면
  - layers.Bidirectional(layers.LSTM(64, return_sequences=True), input_shape=(5, 10))

#### 4-3) 훈련 결과 진단하기
<font color="red">QUIZ :   
a. 현재 모델에 문제점이 있나요?   
b. 문제가 나타나고 있다면 이에 대한 해결 방안을 제시해 보세요. 
</font>
"""

import matplotlib.pyplot as plt

def plot_graphs(history, string):
  plt.plot(history.history[string])
  plt.plot(history.history['val_'+string])
  plt.xlabel("Epochs")
  plt.ylabel(string)
  plt.legend([string, 'val_'+string])
  plt.show()
  
plot_graphs(history, "accuracy")
plot_graphs(history, "loss")

"""## Step 5. Inference 실행하기"""

""" 훈련된 모델로 다시 예측해보기 """

def inference(mymodel, sentence):
  # 1. tokenizer로 문장 파싱
  parsed_sent = tokenize(sentence)
  input_id = []

  # 2. vocab_dict를 이용해 인덱스로 변환
  for word in parsed_sent:
    if word in vocab_dict: input_id.append(vocab_dict[word])
    else: input_id.append(vocab_dict["[OOV]"])
  
  # 단일 문장 추론이기 때문에 패딩할 필요가 없음 
  score = mymodel.predict(np.array([input_id])) 

  print("** INPUT:", sentence)
  print("   -> 부정: {:.2f} / 긍정: {:.2f}".format(score[0][0],score[0][1]))

sentence1 = "시간 가는 줄 알고 봤습니다."
sentence2 = "안보면 후회ㅠㅠ..."
inference(model, sentence1)
inference(model, sentence2)

# 원하는 문장에 대해 추론해 보세요
inference(model, "박서준이 다했따")
inference(model, "꿀잠 잤습니다")

"""# # 3. 나만의 모델 만들어보기

# 실습 MISSION #16
>  LSTM, Dense layer 등을 자유롭게 활용해서 자신만의 모델을 만들고 
이후 TEST 데이터에 대해 최종 성능을 비교해보세요
</font>
"""

tf.keras.backend.clear_session()
 
# 1. 모델 구현하기
model2 = tf.keras.Sequential([
                              # MISSION 작성 #
                              tf.keras.layers.Embedding(vocab_size, 150),
                              tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
                              # tf.keras.layers.Dropout(rate = 0.3),
                              tf.keras.layers.Dense(100, activation='relu'),
                              tf.keras.layers.Dense(2, activation='softmax')
                              ################                 
])

layers.Bidirectional(layers.LSTM(64, return_sequences=True), 
                               input_shape=(5, 10))


# 2. optimizer, loss 선택하기
model2.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# 3. 모델 훈련하기
num_epochs = 1
history = model2.fit(train_input_ids, train_label_ids, epochs=num_epochs, validation_data=(val_input_ids, val_label_ids), verbose=2)

# 4. 모델 진단하기

plot_graphs(history, "accuracy")
plot_graphs(history, "loss")

# 5. 테스트 데이터에 대해 평가하기

model2.evaluate(test_input_ids, test_label_ids, verbose=2)

# 샘플 예제에 대해 추론해 보세요 

inference(model2, "물이 반도 안남았다")  #부정
inference(model2, "물이 반이나 남았다")  #긍정
inference(model2, "죄송하지만 혹시 실례가 안된다면 꺼져주실수 있으신지ㅎㅎ?") #부정
inference(model2, "잘하는 짓이다") #부정
inference(model2, "가게 외관은 구린데 맛은 ㅇㅈ") #긍정
inference(model2, "ㄷㄷ 간만에 갓띵작 ㄷㄷㄷ") #긍정
inference(model2, "주인공 커여워 ㅠㅠ") #긍정
inference(model2, "OTL") #부정

