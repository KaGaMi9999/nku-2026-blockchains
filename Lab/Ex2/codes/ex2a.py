from sys import exit
from bitcoin.core.script import *
from bitcoin.wallet import CBitcoinSecret

from utils import *
from config import my_private_key, my_public_key, my_address, faucet_address
from ex1 import send_from_P2PKH_transaction


cust1_private_key = CBitcoinSecret(
    'cVagQk5G9RDw1fGUZB7wz6XHtRmuQbFTRiS5Q5VmRqfKvpCTTGkv')
cust1_public_key = cust1_private_key.pub

cust2_private_key = CBitcoinSecret(
    'cSe7i5qZAytxrLZz3RfDLWpod72K4dw5kbmrCLEXPHse8UvfTYMw')
cust2_public_key = cust2_private_key.pub

cust3_private_key = CBitcoinSecret(
    'cNeiTGmMwC1jRTmuGL1UAzrL9KmmVqySz9aZ7wbNg8APt6nvcbCS')
cust3_public_key = cust3_private_key.pub


######################################################################
# TODO: Complete the scriptPubKey implementation for Exercise 2

# You can assume the role of the bank for the purposes of this problem
# and use my_public_key and my_private_key in lieu of bank_public_key and
# bank_private_key.

# 2-of-4 多签的赎回脚本（redeem script）：银行 + 三个客户中的任意一个共同签名即可赎回。
# OP_CHECKMULTISIG 的规则：脚本里公钥的顺序决定了解锁脚本里签名的顺序，
# 因此这里统一约定顺序为 银行 -> 客户1 -> 客户2 -> 客户3。
ex2a_redeemScript = CScript([
    OP_2,              # 需要 2 个有效签名（银行 + 任意一个客户）
    my_public_key,     # 银行公钥（即自己的公钥）
    cust1_public_key,  # 客户1公钥
    cust2_public_key,  # 客户2公钥
    cust3_public_key,  # 客户3公钥
    OP_4,              # 共有 4 个公钥
    OP_CHECKMULTISIG,  # 校验多签名
])


ex2a_txout_scriptPubKey = ex2a_redeemScript.to_p2sh_scriptPubKey()
######################################################################

if __name__ == '__main__':
    ######################################################################
    # TODO: set these parameters correctly
    amount_to_send = 0.00009
    txid_to_spend = (
        'a94c1641cd0311ed2b6e33599829a128f597774e71dedb71bfe2e1699878ccb9')
    utxo_index = 1
    ######################################################################

    response = send_from_P2PKH_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        ex2a_txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
