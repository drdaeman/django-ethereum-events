import json
from django.test import TestCase
from django.conf import settings
from web3 import Web3, EthereumTesterProvider
#from web3.providers.eth_tester import EthereumTesterProvider
from eth_tester import EthereumTester
from .test_event_receivers import data
from ..event_listener import EventListener
from ..models import Daemon

TEST_CONTRACT_ABI = """
    [
      {
        "constant": false,
        "inputs": [
          {
            "name": "_id",
            "type": "bytes32"
          }
        ],
        "name": "deposit",
        "outputs": [],
        "payable": true,
        "stateMutability": "payable",
        "type": "function"
      },
      {
        "anonymous": false,
        "inputs": [
          {
            "indexed": true,
            "name": "_from",
            "type": "address"
          },
          {
            "indexed": true,
            "name": "_id",
            "type": "bytes32"
          },
          {
            "indexed": false,
            "name": "_value",
            "type": "uint256"
          }
        ],
        "name": "Deposit",
        "type": "event"
      }
    ]
"""

TEST_CONTRACT_BYTECODE = "6060604052341561000f57600080fd5b5b60da8061001e6000396000f30060606040526" \
                         "000357c0100000000000000000000000000000000000000000000000000000000900463" \
                         "ffffffff168063b214faa514603d575b600080fd5b60556004808035600019169060200" \
                         "190919050506057565b005b80600019163373ffffffffffffffffffffffffffffffffff" \
                         "ffffff167f19dacbf83c5de6658e14cbf7bcae5c15eca2eedecf1c66fbca928e4d351be" \
                         "a0f346040518082815260200191505060405180910390a35b505600a165627a7a723058" \
                         "2048744ea8b6642d6c29c8c4a2a89259824bbf973168b4718947dc385c9b0fb8970029"


class EventListenerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        abi = json.loads(TEST_CONTRACT_ABI)
        #cls.eth_tester = EthereumTester()
        #cls.provider = EthereumTesterProvider(cls.eth_tester)
        cls.provider = EthereumTesterProvider()
        cls.event_listener = EventListener(rpc_provider=cls.provider)
        cls.web3 = cls.event_listener.web3

        # Deploy contract
        cls.contract_factory = cls.web3.eth.contract(abi=abi, bytecode=TEST_CONTRACT_BYTECODE)
        tx_hash = cls.contract_factory.deploy({'from': cls.web3.eth.accounts[0]})
        contract_address = cls.web3.eth.getTransactionReceipt(tx_hash).get('contractAddress')
        cls.contract_factory = cls.web3.eth.contract(contract_address, abi=abi)
        #cls.snapshot = cls.eth_tester.take_snapshot()

        cls.event_listener.decoder.topics_map[cls.event_listener.decoder.topics[0]] = {
            'CONTRACT_ADDRESS': contract_address,
            'EVENT_ABI': abi[1],
            'EVENT_RECEIVER': 'django_ethereum_events.tests.test_event_receivers.DepositEventReceiver'
        }

        cls.event_listener.decoder.watched_addresses = [contract_address]

    def tearDown(self):
        TestCase.tearDown(self)
        # self.eth_tester.revert_to_snapshot(self.snapshot)

    def test_get_pending_blocks(self):
        # Mine a little
        # num_blocks = 5
        num_blocks = 2
        # self.eth_tester.mine_blocks(num_blocks=num_blocks)
        pending_blocks = self.event_listener.get_pending_blocks()
        self.assertEqual(pending_blocks, range(1, num_blocks + 1), 'Pending blocks retrieved')

    def test_update_block_number(self):
        self.event_listener.update_block_number(self.web3.eth.blockNumber)
        d = Daemon.get_solo()
        self.assertEqual(d.block_number, self.web3.eth.blockNumber, 'Block number updated')

    def test_get_logs(self):
        #logs, _ = self.event_listener.get_logs(self.web3.eth.blockNumber)
        #self.assertEqual(logs, [], 'No transaction therefore no logs')

        # Create a transaction
        tx_data = {'from': self.web3.eth.accounts[0], 'value': 1000000000000000000}
        tx_hash = self.contract_factory.transact(tx_data).deposit('0xCAFEBABA')  # deposit 1 ether
        receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        logs, _ = self.event_listener.get_logs(self.web3.eth.blockNumber)
        self.assertEqual(logs, receipt.get('logs'), 'Log retrieved')

    def test_execute(self):
        # Create a transaction
        print(self.event_listener.decoder.topics)
        tx_data = {'from': self.web3.eth.accounts[0], 'value': 1000000000000000000}
        tx_hash = self.contract_factory.transact(tx_data).deposit('0xCAFEBABA')  # deposit 1 ether
        self.event_listener.execute()
        self.assertEqual(len(data), 1, '')