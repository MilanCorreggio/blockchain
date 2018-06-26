
from uuid import uuid4
import requests
from flask import Flask, jsonify, request
import ClassBlockchain
import os,sys
import socket
import requests
import json,re
import random
import platform

ip = sys.argv[1]
noeud = ip+":1111"
# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
user = open("name.txt","r+")
if not user.read():
    name = input("qui êtes vous ?")
    user.write(name)
node_identifier = user.read()
user.close()

#initialisate the blockchain
blockchain = ClassBlockchain.Blockchain()
if(blockchain.nodes == set()):
    blockchain.nodes.add(ip)


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['amount'])
    for node in list(blockchain.nodes):
        active_node = []
        if platform.system()=="Windows":
            response = os.system("ping -n 1 "+node)
        else:
            response = os.system("ping -c 1 "+node)
        if response == 0:
            active_node.append(node)
        else:
            blockchain.nodes.remove(node)
    minor = random.choice(active_node)
    return jsonify(blockchain.minning(minor)),201
    #response = {'message': f'Transaction will be added to Block {index}',"nodes": a }
    #return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


"""@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201"""


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/join', methods=['POST'])
def join():
    values = request.get_json()
    nodes = values.get('nodes')
    
    for node in nodes:
        a = re.match(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",node)
        if a is None:
            return "Error: Please supply a valid node", 400
        blockchain.register_node(node)
    response = {
        'chain': blockchain.chain,
        'transaction':blockchain.current_transactions,
        'nodes':list(blockchain.nodes)
    }
    return jsonify(response), 201
if __name__ == '__main__':
    app.run(host=ip, port=1111)


