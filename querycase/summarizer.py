from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load BART model and tokenizer
model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def summarize_texts(query, texts, max_tokens=3000):
    combined = " ".join(texts).replace("\n", " ")
    input_text = combined[:max_tokens]

    # Tokenize input
    inputs = tokenizer(input_text, return_tensors="pt", max_length=1024, truncation=True)
    
    # Generate summary
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=300,
        min_length=80,
        no_repeat_ngram_size=2,
        forced_bos_token_id=0
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary
