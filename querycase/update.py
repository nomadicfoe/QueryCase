#from querycase.fetch import fetch_new_cases
from querycase.fetch import fetch_new_case_batches
from querycase.embed import embed_and_update_index


'''
def run(max_cases=None):  # Allow unlimited
    print("🔁 Starting QueryCase full pipeline...")
    new_cases = fetch_new_case_batches(max_cases=max_cases)

    try:
        new_cases = fetch_new_case_batches(max_cases=max_cases)
        print(f"📦 fetch_new_cases() returned {len(new_cases)} cases.")
    except Exception as e:
        print(f"❌ fetch_new_case_batches() raised an error: {e}")
        return

    if not new_cases:
        print("✅ No new valid cases found.")
        return

    try:
        embed_and_update_index(new_cases)
        print("✅ QueryCase update complete.")
    except Exception as e:
        print(f"❌ Failed to embed/index: {e}")
'''
def run():
    run_batches(batch_size=50, max_batches=None)

def run_batches(batch_size=50, max_batches=None):
    print("🔁 Starting batch ingestion...")
    batch_count = 0

    for batch in fetch_new_case_batches(batch_size=batch_size):
        print(f"\n📦 Processing batch {batch_count + 1} with {len(batch)} cases")
        embed_and_update_index(batch)
        batch_count += 1

        if max_batches and batch_count >= max_batches:
            print("⏹️ Max batches reached — stopping.")
            break

    print(f"✅ Completed {batch_count} batch(es).")

if __name__ == "__main__":
    run()
