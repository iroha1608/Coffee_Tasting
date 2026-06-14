import secrets
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

JST = ZoneInfo("Asia/Tokyo")

PREFECTURES = [
    "北海道",
    "青森県",
    "岩手県",
    "宮城県",
    "秋田県",
    "山形県",
    "福島県",
    "茨城県",
    "栃木県",
    "群馬県",
    "埼玉県",
    "千葉県",
    "東京都",
    "神奈川県",
    "新潟県",
    "富山県",
    "石川県",
    "福井県",
    "山梨県",
    "長野県",
    "岐阜県",
    "静岡県",
    "愛知県",
    "三重県",
    "滋賀県",
    "京都府",
    "大阪府",
    "兵庫県",
    "奈良県",
    "和歌山県",
    "鳥取県",
    "島根県",
    "岡山県",
    "広島県",
    "山口県",
    "徳島県",
    "香川県",
    "愛媛県",
    "高知県",
    "福岡県",
    "佐賀県",
    "長崎県",
    "熊本県",
    "大分県",
    "宮崎県",
    "鹿児島県",
    "沖縄県",
]

MAX_COFFEES = 20


class Roaster(Base):
    __tablename__ = "roasters"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    company_name_kana = Column(String, nullable=False)
    contact_person = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    prefecture = Column(String, nullable=False)
    access_hash = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(JST))

    coffees = relationship("Coffee", back_populates="roaster")

    @staticmethod
    def new_hash() -> str:
        return secrets.token_urlsafe(16)


class Coffee(Base):
    __tablename__ = "coffees"

    id = Column(Integer, primary_key=True, index=True)
    roaster_id = Column(Integer, ForeignKey("roasters.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(JST))

    roast_level = Column(String, nullable=True)    # 焙煎度
    acidity = Column(String, nullable=True)        # 酸味
    body = Column(String, nullable=True)           # ボディ
    sweetness = Column(String, nullable=True)      # 甘味
    package_size = Column(String, nullable=True)   # 販売パッケージサイズ
    category = Column(String, nullable=True)       # 審査するコーヒー部門
    roast_date = Column(String, nullable=True)     # 焙煎日（日付もハッカソンならStringで保存するのが一番安全！）

    price = Column(Integer, nullable=True)         # 小売価格
    annual_volume = Column(Integer, nullable=True) # 年間焙煎量

    roaster = relationship("Roaster", back_populates="coffees")
    results = relationship("Result", back_populates="coffee")


class Taster(Base):
    __tablename__ = "taster"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_kana = Column(String, nullable=False)
    prefecture = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    company_name = Column(String, nullable=False)
    access_hash = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(JST))

    results = relationship("Result", back_populates="taster")

    @staticmethod
    def new_hash() -> str:
        return secrets.token_urlsafe(16)


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    taster_id = Column(Integer, ForeignKey("taster.id"), nullable=False)
    coffee_id = Column(Integer, ForeignKey("coffees.id"), nullable=False)

    # 審査前は未入力のため nullable=True
    appearance_score = Column(Integer, nullable=True) # 外観: 1-3点
    aroma_score = Column(Integer, nullable=True)      # 香り: 1-7点
    flavor_score = Column(Integer, nullable=True)     # 味わい: 1-10点

    # リレーションシップ
    taster = relationship("Taster", back_populates="results")
    coffee = relationship("Coffee", back_populates="results")

    # DBレベルでのスコア範囲制約
    __table_args__ = (
        CheckConstraint('appearance_score >= 1 AND appearance_score <= 3', name='chk_appearance'),
        CheckConstraint('aroma_score >= 1 AND aroma_score <= 7', name='chk_aroma'),
        CheckConstraint('flavor_score >= 1 AND flavor_score <= 10', name='chk_flavor'),
    )
