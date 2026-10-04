import json
import os
from openai import OpenAI

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "Y0URS KEY") 
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

VERIFY_PROMPT = """
You are an AI auditor. Compare the Original and Mutated messages.
Is there a meaningful distortion in facts, intent, or attribution?
Output strictly JSON:
{
    "is_distorted": boolean,
    "brief_summary": "1 sentence explaining the change or why it's identical"
}
When in doubt, set "is_distorted": false.
"""

def fast_verify(original, mutated):
    pass 

DEEP_JUDGE_PROMPT = """
You are an expert cognitive linguist and AI auditor. Analyze the mutation between the Original and Mutated messages.
CRITICAL RULE: When in doubt, choose "False_Positive". It is better to miss a subtle distortion than to invent one.

Output STRICTLY in JSON without markdown formatting or escaped quotes in values. Schema:
{
    "distortion_type": "Choose EXACTLY ONE category from the list below",
    "direction": "hardened | softened | shifted | none",
    "absurdity_score": "Integer 1-10. 10 = meaning inverted or safety-critical detail fabricated (e.g., a dropped negation). 1 = trivial rewording.",
    "evidence": "Quote the exact phrase that changed from both original and mutated texts.",
    "reasoning": "1 sentence explaining the classification.",
    "chain_summary": "A high-level summary of the trajectory (e.g., 'a routine notice hardened into an urgent alert')."
}

CATEGORIES (MECE):
1. Entity_Hallucination: Names, IDs, tools, or objects are completely fabricated or swapped.
2. Detail_Inflation: Adding new factual content (specific numbers, names, times) that did not exist.
3. Context_Escalation: Amplifying the emotional tone, urgency, or stakes WITHOUT adding new facts.
4. Semantic_Loss: Core intent, context, or collaborative willingness is completely dropped.
5. Attribution_Shift: Responsibility diffusion (e.g., changing "I decided" to "We agreed").
6. Correction: The mutated message actually fixes an error or clarifies ambiguity from the original seed.
7. False_Positive: Meaning is basically the same. PREFER THIS WHEN UNCERTAIN. If chosen, absurdity_score MUST be <= 2.
"""

def deep_analyze(original, mutated):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": DEEP_JUDGE_PROMPT},
                {"role": "user", "content": f"Original:\n{original}\n\nMutated:\n{mutated}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Loading raw mutations...")
    try:
        with open("raw_mutations.json", "r", encoding="utf-8") as f:
            all_mutations = json.load(f)
    except FileNotFoundError:
        print("Error: raw_mutations.json not found! Please run tracer.py first.")
        exit()
        
    test_batch = all_mutations[:100] 
    
    final_results = []
    
    print(f"\n[Pipeline] Starting analysis on {len(test_batch)} cases with real-time saving...")
    
    for idx, item in enumerate(test_batch):
        original = item['source_text']
        mutated = item['mutated_text']
        
        if item['similarity'] <= 0.65: 
            print(f"\n[Call B] Deep Analyzing Case {idx+1} (Sim: {item['similarity']})...")
            analysis = deep_analyze(original, mutated)
            
            if "error" in analysis:
                print(f"  -> API Error skipped: {analysis['error']}")
                continue

            raw_score = analysis.get("absurdity_score", 0)
            try:
                score = int(raw_score)
            except (ValueError, TypeError):
                score = 0  
            
            if analysis.get("distortion_type") != "False_Positive" and score > 2:
                final_record = {
                    "similarity": item['similarity'],
                    "original": original,
                    "mutated": mutated,
                    "analysis": analysis
                }
                final_results.append(final_record)
                print(f"  -> Caught a {analysis.get('distortion_type')}! Score: {score}")
                
                with open("final_insights.json", "w", encoding="utf-8") as f:
                    json.dump(final_results, f, indent=2, ensure_ascii=False)
                    
    print(f"\n[Success] Pipeline finished! Extracted {len(final_results)} high-value mutations.")
    print("All structured evidence is securely saved in final_insights.json.")