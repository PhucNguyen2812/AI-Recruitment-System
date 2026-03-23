# ============================================================
# tests/test_ai_pipeline.py
# Unit tests cho AI Pipeline: NLP Service
# ============================================================
import pytest
from app.services.nlp_service import detect_language, extract_features_for_rf, features_to_list, FEATURE_COLUMNS

class TestNLPService:
    def test_detect_language_vietnamese(self):
        text = "Lập trình viên phần mềm, kinh nghiệm lập trình Frontend với React, Backend với Node.js."
        assert detect_language(text) == "vi"

    def test_detect_language_english(self):
        text = "Software engineer with experience in Frontend React and Backend Node.js."
        assert detect_language(text) == "en"

    def test_detect_language_empty(self):
        assert detect_language("") == "en"

    def test_extract_features_for_rf(self):
        text = "Lập trình viên web development, email: nguyenvan@email.com. Số điện thoại: 0912345678. Tôi giỏi python, java, react."
        # Has words, email, phone, languages, keywords (python, java, react, web development, lập trình viên)
        features = extract_features_for_rf(text, position="IT_Intern")
        
        assert features["total_words"] > 5
        assert features["has_email"] == 1
        assert features["has_phone"] == 1
        assert features["language"] == 1 # vi
        assert features["keyword_count"] > 0
        assert features["position_keyword_count"] > 0
        
        # Test serialization order
        vector = features_to_list(features)
        assert len(vector) == len(FEATURE_COLUMNS)
        assert vector[5] == 1.0 # has_email is index 5
        assert vector[6] == 1.0 # has_phone is index 6
        assert vector[7] == 1.0 # language is index 7

    def test_extract_features_gibberish(self):
        text = "a b c d e f g h i j k l m x y z"
        features = extract_features_for_rf(text)
        assert features["gibberish_ratio"] == 1.0
        assert features["keyword_count"] == 0
        assert features["has_email"] == 0

