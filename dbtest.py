from database import SessionLocal, engine, Base
from models import Roaster, Coffee
import random
import json
import sys

def make_sample():
    # テーブルが存在しない場合に作成
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 既存データの確認（二重登録防止のため簡易的にチェック）
        if db.query(Roaster).first():
            print("Database already has data. Skipping sample creation.")
            return

        print("Creating sample data...")

        # Roaster 1
        roaster1 = Roaster(
            company_name="青空コーヒー",
            company_name_kana="アオゾラコーヒー",
            contact_person="田中 太郎",
            address="東京都渋谷区1-2-3",
            phone="03-1234-5678",
            email="aozora@example.com",
            prefecture="東京都",
            access_hash=Roaster.new_hash()
        )
        db.add(roaster1)
        db.flush() # IDを確定させる

        # Coffee for Roaster 1
        db.add(Coffee(roaster_id=roaster1.id, name="エチオピア・イルガチェフェ"))
        db.add(Coffee(roaster_id=roaster1.id, name="ブラジル・サントス"))

        # Roaster 2
        roaster2 = Roaster(
            company_name="森の焙煎所",
            company_name_kana="モリノバイセンジョ",
            contact_person="佐藤 花子",
            address="長野県北佐久郡軽井沢町4-5-6",
            phone="0267-12-3456",
            email="mori@example.com",
            prefecture="長野県",
            access_hash=Roaster.new_hash()
        )
        db.add(roaster2)
        db.flush()

        # Coffee for Roaster 2
        db.add(Coffee(roaster_id=roaster2.id, name="マンデリン G1"))

        db.commit()
        print("Sample data created successfully.")
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

def list_all_data():
    # テーブルが存在しない場合に作成
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        coffees = db.query(Coffee).all()
        print(type(coffees))
        random.shuffle(coffees)
        if not coffees:
            print("No coffees found in the database.")
        else:
            print(f"{'ID':<4} | {'Roaster ID':<10} | {'Coffee Name':<30} | {'Created At'}")
            print("-" * 100)
            for coffee in coffees:
                print(f"{coffee.id:<4} | {coffee.roaster_id:<10} | {coffee.name:<30} | {coffee.created_at}")

    finally:
        db.close()

def export_json(filename="coffee_data.json"):
     # テーブルが存在しない場合に作成
     Base.metadata.create_all(bind=engine)

     db = SessionLocal()
     try:
         roasters = db.query(Roaster).all()
         data = []
         for r in roasters:
             data.append({
                 "id": r.id,
                 "company_name": r.company_name,
                 "email": r.email,
                 "coffees": [c.name for c in r.coffees]
             })

         # convert_json_to_csv.py が期待する構造 {"data": [...]} に合わせる
         output = {"data": data}

         with open(filename, "w", encoding="utf-8") as f:
             json.dump(output, f, ensure_ascii=False, indent=4)
         print(f"Exported data to {filename}")
     finally:
         db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "sample":
        make_sample()
    if len(sys.argv) > 1 and sys.argv[1] == "json":
        export_json()

    list_all_data()
