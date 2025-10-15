from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List
import json
from pathlib import Path


@dataclass
class FAQ:
	id: str
	question: str
	answer: str


class FAQRepository:
	def __init__(self, path: str | Path):
		self.path = Path(path)
		self._faqs: List[FAQ] = []

	def load(self) -> List[FAQ]:
		self._faqs.clear()
		with self.path.open("r", encoding="utf-8") as f:
			for line in f:
				if not line.strip():
					continue
				obj = json.loads(line)
				self._faqs.append(FAQ(id=obj["id"], question=obj["question"], answer=obj["answer"]))
		return list(self._faqs)

	def all(self) -> Iterable[FAQ]:
		return list(self._faqs)

	def is_loaded(self) -> bool:
		return len(self._faqs) > 0
