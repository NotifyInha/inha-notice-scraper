import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# nltk의 불용어 사전을 다운로드합니다.
import nltk

from DataModel import Notice


def preprocess_text(text):
    # 불필요한 문자 제거
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # 모든 텍스트를 소문자로 변환
    text = text.lower()
    
    # 불용어 제거
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    text = ' '.join([word for word in words if word not in stop_words])
    return text


def extract_keywords(texts, max_features=10):
    # 최대 특성(단어) 수를 제한하여 TF-IDF 벡터라이저를 생성합니다.
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # 각 문서의 키워드(특성 이름)를 추출합니다.
    feature_names = vectorizer.get_feature_names_out()
    
    # 각 문서별로 가장 중요한 키워드를 추출합니다.
    keywords = [feature_names[tfidf_matrix[i].toarray().flatten().argsort()[-max_features:][::-1]] for i in range(tfidf_matrix.shape[0])]
    
    return keywords
def determine_similarity(keywords1, keywords2, threshold=0.5):
    # 두 키워드 리스트의 교집합을 구하고, 각 리스트의 고유 키워드 수로 나눈 후 평균을 구합니다.
    common_keywords = set(keywords1) & set(keywords2)
    similarity = (len(common_keywords) / len(set(keywords1 + keywords2)))
    
    # 유사도가 임계값 이상이면 True, 그렇지 않으면 False를 반환합니다.
    return similarity >= threshold


def check_duplicate(data :Notice, data2 :Notice):
    nltk.download('punkt')
    nltk.download('stopwords')
    doc1 = data.content
    doc2 = data2.content
    # 텍스트 전처리
    preprocessed_doc1 = preprocess_text(doc1)
    preprocessed_doc2 = preprocess_text(doc2)

    # 핵심 키워드 추출
    keywords = extract_keywords([preprocessed_doc1, preprocessed_doc2])

    # 주제 일치성 판별
    is_similar = determine_similarity(keywords[0], keywords[1])
    return is_similar
