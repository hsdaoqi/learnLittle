"""sentence-transformers CrossEncoder 必须走 predict，不能调 FlagEmbedding 的 compute_score。"""

from app.rag.retriever import rerank_hits, set_cross_encoder, set_rerank_fn


class _FakeSentenceTransformerCrossEncoder:
    def __init__(self, scores):
        self.scores = scores
        self.pairs = None

    def predict(self, pairs):
        self.pairs = pairs
        return self.scores


def test_sentence_transformers_cross_encoder_uses_predict():
    set_rerank_fn(None)
    model = _FakeSentenceTransformerCrossEncoder([0.2, 0.8])
    set_cross_encoder(model)
    ranked = rerank_hits("q", [{"content": "low"}, {"content": "high"}])
    assert ranked[0]["content"] == "high"
    assert model.pairs == [("q", "low"), ("q", "high")]
    assert ranked[0]["rerank_score"] == 0.8
