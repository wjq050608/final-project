# utils/keyword_extractor.py
import string

import nltk
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


class KeywordExtractor:
    def __init__(self, language: str = 'english'):
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('punkt_tab')
        nltk.download('averaged_perceptron_tagger_eng')
        self.stop_words = set(stopwords.words(language))
        self.punctuation = set(string.punctuation)


    def extract_keywords(self, text: str, top_n: int = 15) :
        """Keywords are extracted based on TF-IDF and part-of-speech tagging"""
        # Preprocessing: Word segmentation + filtering
        tokens = self._preprocess_text(text)
        # Calculate TF-IDF
        tfidf = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf_matrix = tfidf.fit_transform([" ".join(tokens)])
        feature_names = tfidf.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        # Sort by TF-IDF score
        keywords_with_scores = sorted(
            zip(feature_names, scores), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in keywords_with_scores[:top_n]]

    def _preprocess_text(self, text: str) :
        """Text preprocessing: word segmentation, word removal, noun retention"""
        tokens = word_tokenize(text.lower())
        tagged = pos_tag(tokens)
        # Keep nouns (NN/NNP/NNS/NNPS) without stopping words/punctuation
        filtered = [
            word for word, pos in tagged
            if pos in ['NN', 'NNS', 'NNP', 'NNPS'] and
            word not in self.stop_words and
            word not in self.punctuation
        ]
        return filtered

# 示例用法
if __name__ == "__main__":
    extractor = KeywordExtractor()
    sample_text = "The Transport Layer ensures end-to-end communication..."
    keywords = extractor.extract_keywords(sample_text)
    print("Top Keywords:", keywords)