# ============================================================
# app/services/nlp_service.py
# NLP Service: Bóc tách text từ PDF + Keyword Matching song ngữ
# ============================================================
import io
import re
import logging
from typing import Optional

import pdfplumber

logger = logging.getLogger("error")

# ─────────────────────────────────────────────────────────────
# KEYWORD POOLS — Phân biệt rõ ràng CV hợp lệ và CV rác
# Dùng chính xác từ khóa đã dùng khi generate synthetic data
# ─────────────────────────────────────────────────────────────

# Tiếng Anh — IT Intern keywords
_KEYWORDS_IT_EN = {
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust",
    "html", "css", "react", "vue", "angular", "node.js", "nodejs", "express",
    "django", "flask", "fastapi", "spring", "laravel",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "git", "docker", "kubernetes", "linux", "aws", "azure", "gcp",
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
    "data structures", "algorithms", "oop", "api", "restful", "microservices",
    "software engineer", "developer", "programmer", "it intern", "backend", "frontend",
    "full stack", "devops", "cloud", "database", "web development",
    "artificial intelligence", "computer science", "information technology",
}

# Tiếng Anh — Marketing Intern keywords
_KEYWORDS_MARKETING_EN = {
    "marketing", "digital marketing", "seo", "sem", "social media", "content",
    "copywriting", "branding", "advertising", "campaign", "analytics",
    "google analytics", "facebook ads", "instagram", "tiktok", "email marketing",
    "market research", "customer", "audience", "engagement", "conversion",
    "kpi", "roi", "crm", "hubspot", "mailchimp", "canva", "adobe",
    "photoshop", "illustrator", "video editing", "graphic design",
    "communications", "public relations", "pr", "media", "influencer",
    "e-commerce", "shopify", "woocommerce", "affiliate", "lead generation",
    "marketing intern", "brand", "strategy",
}

# Tiếng Việt — IT Intern keywords
_KEYWORDS_IT_VI = {
    "lập trình", "phát triển phần mềm", "kỹ thuật phần mềm", "lập trình viên",
    "cơ sở dữ liệu", "thuật toán", "cấu trúc dữ liệu", "máy học",
    "trí tuệ nhân tạo", "mạng máy tính", "bảo mật", "điện toán đám mây",
    "giao diện web", "front-end", "back-end", "toàn stack", "microservice",
    "hệ điều hành", "linux", "kiểm thử phần mềm", "tích hợp liên tục",
    "thực tập it", "thực tập công nghệ", "kỹ sư phần mềm", "intern it",
}

# Tiếng Việt — Marketing Intern keywords
_KEYWORDS_MARKETING_VI = {
    "tiếp thị", "marketing", "truyền thông", "quảng cáo", "thương mại điện tử",
    "quản lý thương hiệu", "nội dung số", "mạng xã hội", "seo", "phân tích dữ liệu",
    "chiến dịch", "khách hàng", "chuyển đổi", "phễu bán hàng", "email marketing",
    "quảng cáo google", "facebook ads", "thiết kế đồ họa", "video marketing",
    "thực tập marketing", "intern marketing", "chăm sóc khách hàng",
    "nghiên cứu thị trường",
}

# Gộp per position
_KEYWORDS_IT = _KEYWORDS_IT_EN | _KEYWORDS_IT_VI
_KEYWORDS_MARKETING = _KEYWORDS_MARKETING_EN | _KEYWORDS_MARKETING_VI
_ALL_VALID_KEYWORDS = _KEYWORDS_IT | _KEYWORDS_MARKETING

# Map vị trí -> keyword set
POSITION_KEYWORDS: dict[str, set[str]] = {
    "IT_Intern": _KEYWORDS_IT,
    "Marketing_Intern": _KEYWORDS_MARKETING,
}

# ─────────────────────────────────────────────────────────────
# AHP CRITERIA KEYWORDS (Phase 2)
# ─────────────────────────────────────────────────────────────

AHP_KEYWORDS = {
    "ky_thuat": {
        "en": {
            "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust",
            "sql", "mysql", "postgresql", "mongodb", "redis", "react", "vue", "angular",
            "node.js", "express", "django", "flask", "fastapi", "spring", "git", "docker",
            "kubernetes", "aws", "azure", "gcp", "linux", "api", "restful", "microservices",
            "html", "css", "machine learning", "deep learning", "tensorflow", "pytorch"
        },
        "vi": {
            "lập trình", "phát triển phần mềm", "kỹ thuật phần mềm", "cơ sở dữ liệu",
            "thuật toán", "cấu trúc dữ liệu", "máy học", "trí tuệ nhân tạo", "mạng máy tính",
            "bảo mật", "điện toán đám mây", "giao diện web", "front-end", "back-end",
            "toàn stack", "hệ điều hành", "kiểm thử phần mềm", "tích hợp liên tục"
        }
    },
    "hoc_van": {
        "en": {
            "university", "bachelor", "master", "phd", "gpa", "degree", "diploma",
            "academic", "scholarship", "dean's list", "honors", "graduation", "college",
            "education", "certified", "certification", "coursework", "thesis"
        },
        "vi": {
            "đại học", "cử nhân", "thạc sĩ", "tiến sĩ", "tốt nghiệp", "học bổng",
            "điểm trung bình", "bằng cấp", "chứng chỉ", "cao đẳng", "giáo dục",
            "luận văn", "nghiên cứu", "học thuật", "khóa học"
        }
    },
    "ngoai_ngu": {
        "en": {
            "english", "ielts", "toeic", "toefl", "japanese", "chinese", "french",
            "german", "korean", "spanish", "jlpt", "hsk", "topik", "bilingual",
            "fluent", "communication skills", "translation", "interpretation"
        },
        "vi": {
            "tiếng anh", "tiếng nhật", "tiếng trung", "tiếng pháp", "tiếng đức",
            "tiếng hàn", "ngoại ngữ", "song ngữ", "thông thạo", "giao tiếp",
            "phiên dịch", "biên dịch", "chứng chỉ ngoại ngữ"
        }
    },
    "tich_cuc": {
        "en": {
            "leader", "leadership", "teamwork", "collaboration", "active", "creative",
            "dynamic", "hard-working", "passionate", "enthusiastic", "self-motivated",
            "problem solving", "critical thinking", "adaptability", "organized", "responsible"
        },
        "vi": {
            "lãnh đạo", "làm việc nhóm", "năng động", "sáng tạo", "nhiệt huyết",
            "chăm chỉ", "cầu tiến", "ham học hỏi", "giải quyết vấn đề", "tư duy phản biện",
            "thích nghi", "trách nhiệm", "tự giác", "đam mê", "cẩn thận"
        }
    }
}


# ─────────────────────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────────────────────

def calculate_raw_scores(text: str) -> dict[str, float]:
    """
    Tính điểm thô (0-10) cho 4 tiêu chí AHP dựa trên Keyword Matching.
    Tự động nhận diện ngôn ngữ để dùng bộ từ khóa phù hợp.
    """
    if not text:
        return {k: 0.0 for k in AHP_KEYWORDS.keys()}

    text_lower = text.lower()
    lang = detect_language(text)
    
    scores = {}
    for criterion, lang_sets in AHP_KEYWORDS.items():
        # Lấy keywords của cả 2 ngôn ngữ để tăng độ phủ (Bilingual CV)
        keywords = lang_sets["en"] | lang_sets["vi"]
        
        # Đếm số lượng keyword xuất hiện trong text
        match_count = sum(1 for kw in keywords if kw in text_lower)
        
        # Normalize sang thang điểm 10
        # Giả định: 5 keywords = 10 điểm (Intern level)
        raw_score = (match_count / 5.0) * 10.0
        scores[criterion] = round(min(raw_score, 10.0), 2)
        
    return scores


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Bóc tách toàn bộ text từ PDF bytes bằng pdfplumber.
    Trả về chuỗi text thuần, đã normalize whitespace.
    Trả về chuỗi rỗng "" nếu không đọc được.
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            full_text = "\n".join(pages_text)
            # Normalize: collapse whitespace, lowercase
            full_text = re.sub(r"\s+", " ", full_text).strip()
            return full_text
    except Exception as e:
        logger.error("extract_text_from_pdf failed: %s", str(e))
        return ""


def detect_language(text: str) -> str:
    """
    Tự động phát hiện ngôn ngữ của văn bản.
    Trả về: 'vi' (Tiếng Việt) hoặc 'en' (Tiếng Anh, default mọi ngôn ngữ khác).

    Dùng cách đơn giản và ổn định: đếm Vietnamese diacritics characters.
    Ngưỡng: nếu >5% ký tự là dấu tiếng Việt -> 'vi', ngược lại -> 'en'.
    """
    if not text:
        return "en"

    # Ký tự đặc trưng tiếng Việt (có dấu)
    vi_pattern = re.compile(
        r"[àáạảãăắằặẳẵâấầậẩẫđèéẹẻẽêếềệểễìíịỉĩòóọỏõôốồộổỗơớờợởỡùúụủũưứừựửữỳýỵỷỹ"
        r"ÀÁẠẢÃĂẮẰẶẲẴÂẤẦẬẨẪĐÈÉẸẺẼÊẾỀỆỂỄÌÍỊỈĨÒÓỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÙÚỤỦŨƯỨỪỰỬỮỲÝỴỶỸ]",
        re.UNICODE
    )
    vi_chars = len(vi_pattern.findall(text))
    total_chars = len(text.replace(" ", ""))

    if total_chars == 0:
        return "en"

    vi_ratio = vi_chars / total_chars
    return "vi" if vi_ratio > 0.05 else "en"


def extract_features_for_rf(text: str, position: Optional[str] = None) -> dict:
    """
    Trích xuất feature vector từ text CV để đưa vào Random Forest.

    Features:
    - total_words: Tổng số từ trong CV
    - unique_words: Số từ unique
    - text_length: Độ dài text
    - keyword_count: Số keyword chuyên ngành match được
    - keyword_ratio: Tỷ lệ keyword / tổng từ
    - has_email: Có địa chỉ email không
    - has_phone: Có số điện thoại không
    - language: 0=en, 1=vi
    - position_keyword_count: Số keyword đặc thù cho vị trí
    - gibberish_ratio: Tỷ lệ từ quá ngắn (< 2 ký tự) — chỉ số gibberish

    Trả về dict có thể convert sang list/array để sklearn sử dụng.
    """
    text_lower = text.lower()
    words = text_lower.split()

    # Basic stats
    total_words = len(words)
    unique_words = len(set(words))
    text_length = len(text)

    # Language detection
    lang = detect_language(text)
    lang_code = 1 if lang == "vi" else 0

    # Keyword matching — dùng all valid keywords
    matched_all = sum(1 for kw in _ALL_VALID_KEYWORDS if kw in text_lower)
    keyword_ratio = matched_all / max(total_words, 1)

    # Position-specific keywords
    if position and position in POSITION_KEYWORDS:
        position_kws = POSITION_KEYWORDS[position]
        position_keyword_count = sum(1 for kw in position_kws if kw in text_lower)
    else:
        # Nếu không có position, dùng max của 2 tập
        position_keyword_count = max(
            sum(1 for kw in _KEYWORDS_IT if kw in text_lower),
            sum(1 for kw in _KEYWORDS_MARKETING if kw in text_lower),
        )

    # Gibberish detection: tỷ lệ từ rất ngắn (<2 ký tự)
    short_words = sum(1 for w in words if len(w) < 2)
    gibberish_ratio = short_words / max(total_words, 1)

    # Email & phone presence
    has_email = 1 if re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text) else 0
    has_phone = 1 if re.search(r"(\+84|0)[0-9]{8,10}|(\d{3}[-.\s]\d{3}[-.\s]\d{4})", text) else 0

    return {
        "total_words": total_words,
        "unique_words": unique_words,
        "text_length": text_length,
        "keyword_count": matched_all,
        "keyword_ratio": keyword_ratio,
        "has_email": has_email,
        "has_phone": has_phone,
        "language": lang_code,
        "position_keyword_count": position_keyword_count,
        "gibberish_ratio": gibberish_ratio,
    }


# Feature column order — phải consistent khi train và khi predict
FEATURE_COLUMNS = [
    "total_words",
    "unique_words",
    "text_length",
    "keyword_count",
    "keyword_ratio",
    "has_email",
    "has_phone",
    "language",
    "position_keyword_count",
    "gibberish_ratio",
]


def features_to_list(feature_dict: dict) -> list[float]:
    """Chuyển feature dict sang list theo đúng thứ tự FEATURE_COLUMNS."""
    return [float(feature_dict.get(col, 0)) for col in FEATURE_COLUMNS]
