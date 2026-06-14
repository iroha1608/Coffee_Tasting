from sqlalchemy.orm import Session
from sqlalchemy import func
import random

from models import Coffee, Taster, Result


def create_coffee(db: Session, roaster_id: int, name: str, category: str) -> Coffee:
    """指定された部門(category)の最大連番を取得し、+1してコーヒーを登録する"""

    # 同じカテゴリー内の現在の最大シリアルナンバーを取得
    max_serial = db.query(func.max(Coffee.serial_number)).filter(Coffee.category == category).scalar()
    next_serial = (max_serial or 0) + 1

    new_coffee = Coffee(
        roaster_id=roaster_id,
        name=name,
        category=category,
        serial_number=next_serial
    )

    db.add(new_coffee)
    db.commit()
    db.refresh(new_coffee)
    return new_coffee


def execute_matching(db: Session, items_per_taster: int = 12) -> bool:
    """
    全審査員(Taster)にコーヒーをランダムかつ均等に割り当て、Resultレコードを生成する
    """
    tasters = db.query(Taster).all()
    coffees = db.query(Coffee).all()

    if not tasters or len(coffees) < items_per_taster:
        return False

    # 各コーヒーの割り当て回数を記録する辞書（初期値0）
    coffee_counts = {coffee.id: 0 for coffee in coffees}
    results_to_create = []

    for taster in tasters:
        available_coffees = list(coffees)
        # 1. ランダム性を担保
        random.shuffle(available_coffees)

        # 2. 割り当て回数が少ない順に並べ替える（これで差が最大でも1になる）
        available_coffees.sort(key=lambda c: coffee_counts[c.id])

        # 3. 上位 N件を抽出し、Result（審査用レコード）として準備
        assigned_coffees = available_coffees[:items_per_taster]

        for coffee in assigned_coffees:
            results_to_create.append(
                Result(taster_id=taster.id, coffee_id=coffee.id)
            )
            coffee_counts[coffee.id] += 1

    try:
        # バルクインサートで何千件あっても一瞬で保存
        db.add_all(results_to_create)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
