from sys import exit
from bitcoin.core.script import *

from utils import *
from config import my_private_key, my_public_key, my_address, faucet_address
from ex1 import P2PKH_scriptPubKey
from ex2a import (ex2a_txout_scriptPubKey, ex2a_redeemScript, cust1_private_key,
                  cust2_private_key, cust3_private_key)


def multisig_scriptSig(txin, txout, txin_scriptPubKey):
    # P2SH 中，签名必须针对 redeem script（而不是 P2SH 锁定脚本）来计算签名哈希
    bank_sig = create_OP_CHECKSIG_signature(txin, txout, ex2a_redeemScript,
                                             my_private_key)
    cust1_sig = create_OP_CHECKSIG_signature(txin, txout, ex2a_redeemScript,
                                             cust1_private_key)
    ######################################################################
    # TODO: Complete this script to unlock the BTC that was locked in the
    # multisig transaction created in Exercise 2a.
    #
    # OP_CHECKMULTISIG 有一个历史 bug：它会多弹出一个堆栈元素，
    # 因此脚本开头必须先压入一个占位符 OP_0。
    #
    # 赎回条件为 2-of-4，这里选择「银行 + 客户1」这一组合法签名。
    # 签名顺序必须与 redeem script 中的公钥顺序严格一致：
    #   银行公钥排第 1 位 -> 用 bank_sig
    #   客户1公钥排第 2 位 -> 用 cust1_sig
    # （换成 cust2_sig / cust3_sig 也都能赎回，只要顺序对应即可）
    #
    # 因为是 P2SH，最后还必须把整个 redeem script 压栈，供节点校验锁定脚本的哈希。
    return [OP_0, bank_sig, cust1_sig, ex2a_redeemScript]
    ######################################################################


def send_from_multisig_transaction(amount_to_send, txid_to_spend, utxo_index,
                                   txin_scriptPubKey, txout_scriptPubKey):
    txout = create_txout(amount_to_send, txout_scriptPubKey)

    txin = create_txin(txid_to_spend, utxo_index)
    txin_scriptSig = multisig_scriptSig(txin, txout, txin_scriptPubKey)

    new_tx = create_signed_transaction(txin, txout, txin_scriptPubKey,
                                       txin_scriptSig)

    return broadcast_transaction(new_tx)

if __name__ == '__main__':
    ######################################################################
    # TODO: set these parameters correctly
    amount_to_send = 0.00008
    txid_to_spend = 'd3adf29cbff2aaab2d19c2ef2d817d0f1e0e93e771df3fb5ae8057ba9ce55122'
    utxo_index = 0
    ######################################################################

    txin_scriptPubKey = ex2a_txout_scriptPubKey
    txout_scriptPubKey = P2PKH_scriptPubKey(faucet_address)

    response = send_from_multisig_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        txin_scriptPubKey, txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
