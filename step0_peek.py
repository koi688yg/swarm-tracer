import json

def peek_at_data(filepath, num_lines=2):
    print(f"--- Inspecting {filepath} ---")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i in range(num_lines):
                line = f.readline()
                if not line:
                    break
                
                data = json.loads(line)
                
                print(f"\n[Row {i+1} Schema Keys]")
                print(list(data.keys()))
                
                if i == 0:
                    print("\n[Row 1 Full Payload Sample]")
                    print(json.dumps(data, indent=2))
                    
    except FileNotFoundError:
        print(f"Error: {filepath} not found in the current directory.")

if __name__ == "__main__":
    peek_at_data("chat_messages.jsonl")