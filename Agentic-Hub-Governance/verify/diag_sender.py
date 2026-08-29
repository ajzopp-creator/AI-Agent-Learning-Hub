import sys
sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")
from schemas import ApprovedSender

try:
    s = ApprovedSender(
        email_address="admin@colibritrader.com",
        sender_name="Colibri Trader",
        date_added="4/26/2026",
        sector=None,
        enabled="TRUE",
    )
    print("PARSED OK:", s)
except Exception as e:
    print("VALIDATION ERROR:")
    print(e)
