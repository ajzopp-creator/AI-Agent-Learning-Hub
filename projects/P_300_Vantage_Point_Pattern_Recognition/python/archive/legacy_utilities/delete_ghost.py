import sqlite3
conn = sqlite3.connect(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db")
# Delete records that have zero features attached to them
conn.execute("DELETE FROM pattern_instances WHERE pattern_instance_id NOT IN (SELECT DISTINCT pattern_instance_id FROM pattern_features)")
conn.commit()
conn.close()