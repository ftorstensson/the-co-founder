import os
import vertexai
from vertexai.generative_models import GenerativeModel, Tool

# 1. Initialize Vertex AI
PROJECT_ID = "vibe-agent-final"
vertexai.init(project=PROJECT_ID, location="us-central1")

def test_official_grounding():
    print("\n--- 🔬 RESEARCH SANDBOX v9.4: LOW-LEVEL SDK BYPASS ---")
    
    # THE "DUMB CODE" BYPASS:
    # Since the SDK's helper methods are using deprecated field names,
    # we use 'from_dict' to physically inject the 'google_search' key
    # that the API error message specifically asked for.
    try:
        print("Bypassing SDK helpers with raw dictionary injection...")
        search_tool = Tool.from_dict({
            "google_search": {} 
        })
        print("✅ SUCCESS: Tool object constructed with 'google_search' key.")
    except Exception as e:
        print(f"❌ FAILED: Even from_dict rejected the key: {e}")
        return

    model = GenerativeModel("gemini-2.5-pro")

    query = "Find the final 2026 Winter Olympics gold medal count for Norway. Provide the source URL."
    print(f"\n1. Query: {query}")
    print("2. Calling Model...")

    try:
        response = model.generate_content(
            query,
            tools=[search_tool]
        )

        print("\n--- FINAL OUTPUT ---")
        print(response.text)
        
        print("\n--- 📜 THE RECEIPTS ---")
        metadata = response.candidates[0].grounding_metadata
        if metadata.grounding_chunks:
            for i, chunk in enumerate(metadata.grounding_chunks):
                if chunk.web:
                    print(f"[{i+1}] {chunk.web.title} -> {chunk.web.uri}")
        
        print("\n🎉 TRIUMPH: The bypass worked. Grounding is live.")

    except Exception as e:
        print(f"\n⚠️ RUNTIME ERROR: {e}")
        if "google_search" in str(e):
            print("The server still rejects the tool config. We may need to use 'google_search_retrieval' inside from_dict as a last resort.")

if __name__ == "__main__":
    test_official_grounding()