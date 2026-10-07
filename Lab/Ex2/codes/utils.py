import requests

from bitcoin.core import b2x, lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from bitcoin.core.script import *
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH


def send_from_custom_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        txin_scriptPubKey, txin_scriptSig, txout_scriptPubKey):
    txout = create_txout(amount_to_send, txout_scriptPubKey)
    txin = create_txin(txid_to_spend, utxo_index)
    new_tx = create_signed_transaction(txin, txout, txin_scriptPubKey,
                                       txin_scriptSig)
    return broadcast_transaction(new_tx)


def create_txin(txid, utxo_index):
    return CMutableTxIn(COutPoint(lx(txid), utxo_index))


def create_txout(amount, scriptPubKey):
    return CMutableTxOut(amount*COIN, CScript(scriptPubKey))


def create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey, seckey):
    tx = CMutableTransaction([txin], [txout])
    sighash = SignatureHash(CScript(txin_scriptPubKey), tx,
                            0, SIGHASH_ALL)
    sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
    return sig


def create_signed_transaction(txin, txout, txin_scriptPubKey,
                              txin_scriptSig):
    tx = CMutableTransaction([txin], [txout])
    txin.scriptSig = CScript(txin_scriptSig)
    VerifyScript(txin.scriptSig, CScript(txin_scriptPubKey),
                 tx, 0, (SCRIPT_VERIFY_P2SH,))
    return tx


def broadcast_transaction(tx):
    raw_transaction = b2x(tx.serialize())
    # ------------------------------------------------------------------
    # 原代码使用的 BlockCypher test3 节点早已停止同步：它的链高度一直卡在
    # 2023-07-05 的 2440465（而真实 testnet3 现在已到 5151360），
    # 所以向它广播会返回 400 "orphaned, missing reference <父交易>"。
    # 这里改为把「原始交易十六进制」POST 给仍在正常同步的 testnet3 公共接口，
    # 按顺序尝试，第一个成功(200)的直接返回；全部失败则返回最后一个响应。
    # 成功时接口返回该交易的 txid（纯文本）。
    # ------------------------------------------------------------------
    headers = {'content-type': 'text/plain'}
    endpoints = [
        'https://mempool.space/testnet/api/tx',
        'https://blockstream.info/testnet/api/tx',
    ]
    response = None
    for url in endpoints:
        response = requests.post(url, headers=headers, data=raw_transaction)
        if response.status_code == 200:
            break
        print('[broadcast] %s 失败: %s %s' %
              (url, response.status_code, response.text[:200]))
    return response
