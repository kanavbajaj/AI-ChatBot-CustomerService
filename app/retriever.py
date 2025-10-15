from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import math
import re

from .faq_loader import FAQ, FAQRepository
from .config import settings


_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)


def _tokenize(text: str) -> List[str]:
	return [t.lower() for t in _WORD_RE.findall(text)]


@dataclass
class RetrievedFAQ:
	faq: FAQ
	score: float


class BM25FAQRetriever:
	def __init__(self, repo: FAQRepository, k1: float = 1.5, b: float = 0.75):
		self.repo = repo
		self.k1 = k1
		self.b = b
		self._faqs: List[FAQ] = []
		self._docs: List[List[str]] = []
		self._df: Dict[str, int] = {}
		self._avgdl: float = 0.0

	def build(self):
		if not self.repo.is_loaded():
			self.repo.load()
		self._faqs = list(self.repo.all())
		self._docs = []
		self._df.clear()
		lengths = []
		for f in self._faqs:
			tokens = _tokenize(f"{f.question} {f.answer}")
			self._docs.append(tokens)
			lengths.append(len(tokens))
			for w in set(tokens):
				self._df[w] = self._df.get(w, 0) + 1
		self._avgdl = (sum(lengths) / len(lengths)) if lengths else 0.0

	def _score(self, qtokens: List[str], idx: int) -> float:
		doc = self._docs[idx]
		dl = len(doc)
		score = 0.0
		# term frequency in doc
		freq: Dict[str, int] = {}
		for w in doc:
			freq[w] = freq.get(w, 0) + 1
		N = len(self._docs) or 1
		for q in qtokens:
			df = self._df.get(q, 0)
			if df == 0:
				continue
			idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
			fq = freq.get(q, 0)
			den = fq + self.k1 * (1 - self.b + self.b * (dl / (self._avgdl or 1.0)))
			score += idf * (fq * (self.k1 + 1)) / (den or 1.0)
		return score

	def retrieve(self, query: str, top_k: int | None = None) -> List[RetrievedFAQ]:
		if not self._docs:
			self.build()
		qtokens = _tokenize(query)
		k = top_k or settings.retriever_top_k
		scores = [(i, self._score(qtokens, i)) for i in range(len(self._docs))]
		scores.sort(key=lambda x: x[1], reverse=True)
		indices = [i for i, s in scores[:k]]
		return [RetrievedFAQ(self._faqs[i], float(scores[j][1])) for j, i in enumerate(indices)]
