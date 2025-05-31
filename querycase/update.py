from querycase.fetch import fetch_new_cases
from querycase.embed import embed_and_update_index

def run(max_cases=5):
    print("🔁 Starting QueryCase update pipeline...")

    try:
        new_cases = fetch_new_cases(max_cases=max_cases)
        print(f"📦 fetch_new_cases() returned {len(new_cases)} cases.")
    except Exception as e:
        print(f"❌ fetch_new_cases() raised an error: {e}")
        return

    if not new_cases:
        print("✅ No new valid cases found.")
        return

    try:
        embed_and_update_index(new_cases)
        print("✅ QueryCase update complete.")
    except Exception as e:
        print(f"❌ Failed to embed/index: {e}")
if __name__ == "__main__":
    run()
