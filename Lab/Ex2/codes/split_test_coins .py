from bitcoin.core.script import *

from utils import *
from config import (my_private_key, my_public_key, my_address,
                    faucet_address)


def split_coins(amount_to_send, txid_to_spend, utxo_index, n):
    txin_scriptPubKey = my_address.to_scriptPubKey()
    txin = create_txin(txid_to_spend, utxo_index)
    txout_scriptPubKey = my_address.to_scriptPubKey()
    txout = create_txout(amount_to_send / n, txout_scriptPubKey)
    tx = CMutableTransaction([txin], [txout]*n)
    sighash = SignatureHash(txin_scriptPubKey, tx,
                            0, SIGHASH_ALL)
    txin.scriptSig = CScript([my_private_key.sign(sighash) + bytes([SIGHASH_ALL]),
                              my_public_key])
    VerifyScript(txin.scriptSig, txin_scriptPubKey,
                 tx, 0, (SCRIPT_VERIFY_P2SH,))
    response = broadcast_transaction(tx)
    print(response.status_code, response.reason)
    print(response.text)

if __name__ == '__main__':
    ######################################################################
    # TODO: set these parameters correctly
    # 待拆分的总金额(BTC) = 该 UTXO 金额 - 手续费
    # 你的 UTXO = 0.00113807 BTC(113807 sat)，这里拆 0.001 BTC，
    # 剩余 0.00113807-0.001 = 0.00013807 BTC(13807 sat) 作为手续费
    amount_to_send = 0.001
    txid_to_spend = (
        '4a519c8caee149e048988bd050eb6a47b716f5f04eaf8fbbb679a033d36d69f3')
    # 属于自身地址的是「1 号输出」（0 号是 faucet 的找零），因此这里填 1
    utxo_index = 1
    n = 10  # 拆成 10 份，每份 0.0001 BTC(10000 sat)
    ######################################################################

    split_coins(amount_to_send, txid_to_spend, utxo_index, n)
