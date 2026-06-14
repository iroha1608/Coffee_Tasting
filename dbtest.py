import json
import random
import sys
import math
from database import SessionLocal, engine, Base
from models import Roaster, Coffee, Taster

def list_coffee_data():
    """すべてのコーヒーデータを取得し、シャッフルしたリストを返す"""
    db = SessionLocal()
    try:
        coffees = db.query(Coffee).all()
        random.shuffle(coffees)
        return coffees
    finally:
        db.close()

def list_taster_data():
    """すべてのテイスターデータを取得し、シャッフルしたリストを返す"""
    db = SessionLocal()
    try:
        tasters = db.query(Taster).all()
        random.shuffle(tasters)
        return tasters
    finally:
        db.close()

def assign_coffees_to_tasters():
    """
    コーヒーをテイスターに割り当てる。
    各テイスターに (コーヒー数 / テイスター数) の端数切り上げ分のコーヒーを割り当てる。
    """
    coffees = list_coffee_data()
    tasters = list_taster_data()
    
    if not coffees or not tasters:
        return {}

    # 1人あたりのコーヒー数（端数切り上げ）
    num_tasters = len(tasters)
    num_coffees = len(coffees)
    per_taster = math.ceil(num_coffees / num_tasters)
    
    print(f"\nAssigning {num_coffees} coffees to {num_tasters} tasters ({per_taster} per taster)...")
    
    assignments = {}
    for i, taster in enumerate(tasters):
        # スライスを使ってコーヒーを切り分ける
        start_idx = i * per_taster
        end_idx = start_idx + per_taster
        assigned = coffees[start_idx:end_idx]
        assignments[taster.id] = {
            "taster": taster,
            "coffees": assigned
        }
        
    return assignments

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
        db.add(Coffee(roaster_id=roaster2.id, name="グアテマラ SHB"))

        # Tasters
        taster1 = Taster(
            name="テイスター 一郎",
            name_kana="テイスター イチロウ",
            prefecture="神奈川県",
            address="横浜市中区1-1",
            phone="045-123-4567",
            email="taster1@example.com",
            company_name="コーヒー評価部",
            access_hash=Taster.new_hash()
        )
        db.add(taster1)
        
        taster2 = Taster(
            name="テイスター 二郎",
            name_kana="テイスター ジロウ",
            prefecture="大阪府",
            address="大阪市北区2-2",
            phone="06-1234-5678",
            email="taster2@example.com",
            company_name="カフェ連盟",
            access_hash=Taster.new_hash()
        )
        db.add(taster2)

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
        print("\n=== Roasters and their Coffees ===")
        roasters = db.query(Roaster).all()

        if not roasters:
            print("No roasters found in the database.")
        else:
            print(f"{'ID':<4} | {'Company Name':<20} | {'Email':<30} | {'Coffees'}")
            print("-" * 100)
            for roaster in roasters:
                coffee_names = ", ".join([c.name for c in roaster.coffees])
                print(f"{roaster.id:<4} | {roaster.company_name:<20} | {roaster.email:<30} | {coffee_names}")

        print("\n=== Coffee Assignments to Tasters ===")
        assignments = assign_coffees_to_tasters()
        if not assignments:
            print("No assignments possible.")
        else:
            print(f"{'Taster Name':<20} | {'Assigned Coffees'}")
            print("-" * 60)
            for aid in assignments:
                entry = assignments[aid]
                t_name = entry["taster"].name
                c_names = ", ".join([c.name for c in entry["coffees"]])
                print(f"{t_name:<20} | {c_names}")

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "sample":
            make_sample()
        elif sys.argv[1] == "json":
            export_json()
    
    list_all_data()
