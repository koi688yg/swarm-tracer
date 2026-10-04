import json
import re
import difflib
from dataclasses import dataclass
from typing import List
from datetime import datetime, timedelta

@dataclass(frozen=True)
class AgentMessage:
    message_id: str
    sender_id: str
    content: str
    created_at: datetime  

def load_and_clean_data(filepath: str) -> List[AgentMessage]:
    print(f"Loading and cleaning data from {filepath}...")
    clean_messages = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            if data.get('speaker_type') != 'agent': continue
                
            content = data.get('content', '')
            if not content or len(content) > 500 or content.strip().startswith('{') or '[REDACTED]' in content:
                continue
                
            msg = AgentMessage(
                message_id=data.get('id'),
                sender_id=data.get('agent_speaker_id'),
                content=content,
                created_at=datetime.strptime(data.get('created_at'), "%Y-%m-%d %H:%M:%S.%f")
            )
            clean_messages.append(msg)
            
    print(f"Sorting {len(clean_messages)} valid messages by timestamp...")
    clean_messages.sort(key=lambda x: x.created_at)
    return clean_messages

def detect_mutations_sliding_window(messages: List[AgentMessage]):
    total_msgs = len(messages)
    print(f"\nUnleashing Temporal Sliding Window on {total_msgs} messages...")
    mutations = []
    
    active_window = []
    
    for i in range(total_msgs):
        if i % 10000 == 0 and i > 0:
            print(f"  ... Processed {i} / {total_msgs} messages. Found {len(mutations)} chains so far.")
            
        msg_b = messages[i]
        time_b = msg_b.created_at
        
        while active_window and (time_b - active_window[0].created_at) > timedelta(hours=12):
            active_window.pop(0)
            
        words_b = set(re.sub(r'[^a-z\s]', '', msg_b.content.lower()).split())
        long_b = {w for w in words_b if len(w) > 5}
        
        for msg_a in active_window:
            if msg_a.sender_id == msg_b.sender_id: continue
            
            words_a = set(re.sub(r'[^a-z\s]', '', msg_a.content.lower()).split())
            if not long_b.intersection(words_a):
                continue
                
            sim = difflib.SequenceMatcher(None, msg_a.content, msg_b.content).ratio()
            
            if 0.55 < sim < 0.85:
                mutations.append({
                    'similarity': round(sim, 2),
                    'source_time': msg_a.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'source_text': msg_a.content,
                    'mutated_time': msg_b.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'mutated_text': msg_b.content
                })
                break  
                
        active_window.append(msg_b)
                
    mutations.sort(key=lambda x: x['similarity'])
    return mutations

if __name__ == "__main__":
    messages = load_and_clean_data("chat_messages.jsonl")
    
    if messages:
        found_mutations = detect_mutations_sliding_window(messages)
        print(f"\n[Success] Found {len(found_mutations)} verified mutation chains across the entire dataset!")
        
        print("\n--- Top 10 Extreme Mutations ---")
        for idx, m in enumerate(found_mutations[:10]):
            print(f"\n[{idx+1}] Similarity: {m['similarity']}")
            print(f"Original : {m['source_text']}")
            print(f"Mutated  : {m['mutated_text']}")
        
        import json
        with open("raw_mutations.json", "w", encoding="utf-8") as f:
            json.dump(found_mutations, f, indent=2, ensure_ascii=False)
        print(f"\n[Export] Successfully saved {len(found_mutations)} raw mutations to raw_mutations.json!")