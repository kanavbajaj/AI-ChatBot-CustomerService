from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .faq_loader import FAQ, FAQRepository
from .config import settings


@dataclass
class RetrievedFAQ:
	faq: FAQ
	score: float


class TfidfFAQRetriever:
	def __init__(self, repo: FAQRepository):
		self.repo = repo
		self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
		self._matrix = None
		self._faqs: List[FAQ] = []

	def build(self):
		if not self.repo.is_loaded():
			self.repo.load()
		self._faqs = list(self.repo.all())
		corpus = [f"{f.question} \n {f.answer}" for f in self._faqs]
		self._matrix = self.vectorizer.fit_transform(corpus)

	def retrieve(self, query: str, top_k: int | None = None) -> List[RetrievedFAQ]:
		if self._matrix is None:
			self.build()
		k = top_k or settings.retriever_top_k
		qv = self.vectorizer.transform([query])
		scores = cosine_similarity(qv, self._matrix)[0]
		indices = scores.argsort()[::-1][:k]
		return [RetrievedFAQ(self._faqs[i], float(scores[i])) for i in indices]
