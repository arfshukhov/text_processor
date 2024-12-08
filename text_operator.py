from typing import List
from models import AddTextModel, Session, TextBase, get_db
import ssl
import nltk
from nltk.corpus import stopwords
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class PipelineNLP:
    def __init__(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        # Загрузка необходимых ресурсов NLTK

        nltk.download("stopwords", download_dir="./nltk_data")
        self.stop_words = set(stopwords.words("russian"))

        self.nlp = spacy.load("ru_core_news_sm")

    def preprocess_text(self, text: str) -> List[str]:
        doc = self.nlp(text.lower())
        tokens = [
            token.lemma_
            for token in doc
            if token.is_alpha and token.lemma_ not in self.stop_words
        ]
        return tokens


class TextSearcher:
    def __init__(self):
        self._pipeline = PipelineNLP()

    @staticmethod
    def get_all_texts(session: Session = next(get_db())) -> list[str]:
        return [str(i.text) for i in session.query(TextBase).all()]

    def __build_tfidf_index(self, texts: List[str]):
        processed_texts = [
            " ".join(self._pipeline.preprocess_text(text)) for text in texts
        ]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(processed_texts)
        return vectorizer, tfidf_matrix

    def find_top_n(self, query: str, n: int = 3) -> List[str]:
        texts = self.get_all_texts()
        vectorizer, tfidf_matrix = self.__build_tfidf_index(texts)
        query_processed = " ".join(self._pipeline.preprocess_text(query))
        query_vector = vectorizer.transform([query_processed])
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-n:][::-1]
        return [texts[i] for i in top_indices]


class TextWriter:
    @classmethod
    def add(cls, text: str, session: Session = next(get_db())) -> AddTextModel | None:
        try:
            t = TextBase(text=text)
            session.add(t)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            res = session.query(TextBase).filter_by(text=text).first()
            if res:
                return AddTextModel.from_orm(res)
            return None
