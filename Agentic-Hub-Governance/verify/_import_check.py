import sys
sys.path.insert(0, r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python')
import config
from infrastructure.mbox_reader import iter_mbox_messages, parse_message_date
from domain.sender_filter import extract_email_address
print('IMPORTS OK')
print('IMAP_ROOT:', config.IMAP_ROOT)
print('DATA_DIR:', config.DATA_DIR)