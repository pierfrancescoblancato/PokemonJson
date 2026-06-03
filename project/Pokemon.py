#import
import requests
import os
import json

class Creature:
    def __init__(self, **data_dict):
        self.id = data_dict.get('id')
        self.name = data_dict.get('name')
        self.height = data_dict.get('height')
        self.weight = data_dict.get('weight')
        self.types = data_dict.get('types', [])
        self.stats = data_dict.get('stats', {})

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'height': self.height,
            'weight': self.weight,
            'types': self.types,
            'stats': self.stats
        }

    def __str__(self):
        return (f"#{self.id} {self.name.upper()} | "
                f"Type: {', '.join(self.types)} | "
                f"HP: {self.stats.get('hp', 'N/A')} | "
                f"Height: {self.height} | Weight: {self.weight}")

class PokemonReader:
    BASE_URL = "https://pokeapi.co/api/v2/pokemon"

    def fetch_as_dict(self, name_or_id):
        url = f"{self.BASE_URL}/{name_or_id}"
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                types = []
                for t in data['types']:
                    types.append(t['type']['name'])
                    
                stats = {}        
                for stats_item in data['stats']:
                    stats[stats_item['stat']['name']] = stats_item['base_stat']

                return {
                    'id': data['id'],
                    'name': data['name'],
                    'height': data['height'],
                    'weight': data['weight'],
                    'types': types,
                    'stats': stats
                }
            
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None

        except requests.exceptions.ConnectionError:
            print("Error: unable to connect. Check your internet connection.")
        except requests.exceptions.Timeout:
            print("Error: the server did not respond in time (timeout).")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} Pokemon '{name_or_id}' not found.")
        except requests.exceptions.RequestException as e:
            print(f"Unexpected network error: {e}")
        except KeyError as e:
            print(f"Error: unexpected API response structure missing key: {e}")
            
        return None

class JSONWriter:
    DIR  = "data/creatures"
    def save(self, data):
        try:
            os.makedirs(self.DIR, exist_ok=True)
            file_path = f"{self.DIR}/{data['name']}.json"
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"File saved: {file_path}")
            return True
        except OSError as e:
            print(f"Error saving file: {e}")
        except KeyError:
            print("Error: the dictionary does not contain the key 'name'.")
        return False

class JSONReader:

    def load(self, name):
        file_path = f"data/creatures/{name}.json"
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
            
        except FileNotFoundError:
            print(f"Error: file '{file_path}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error: the JSON file is malformed: {e}")
        return None

def build_creature(data):
    try:
        return Creature(**data)
    except TypeError as e:
        print(f"Error: data is incompatible with the Creature constructor: {e}")
    return None

def main():
    name_or_id = input("Enter a Pokemon name or ID: ").strip().lower()

    if not name_or_id:
        print("Error: input cannot be empty.")
        return

    reader = PokemonReader()
    api_data = reader.fetch_as_dict(name_or_id)

    if not api_data:
        print("Cannot proceed: data not available.")
        return

    writer = JSONWriter()
    writer.save(api_data)

    creature = build_creature(api_data)
    if creature:
        print("\nCreature created from API:")
        print(creature)

    reload = input("\nDo you want to reload the creature from the JSON file? (y/n): ").strip().lower()
    if reload == 'y':
        file_reader = JSONReader()
        file_data = file_reader.load(api_data['name'])

        if file_data:
            reloaded_creature = build_creature(file_data)
            if reloaded_creature:
                print("\nCreature reloaded from file:")
                print(reloaded_creature)

if __name__ == "__main__":
    main()