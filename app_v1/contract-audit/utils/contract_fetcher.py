import requests

def fetch_contract_source(contract_address, contract_name):
    url = f"https://api.hiro.so/v2/contracts/source/{contract_address}/{contract_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("source")
    else:
        return f"Error: {response.status_code} - {response.text}"

def fetch_function(contract_address, contract_name):
    url = f"https://api.hiro.so/v2/contracts/interface/{contract_address}/{contract_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()  
        return data.get("functions")
    else:
        return f"Error: {response.status_code} - {response.text}"