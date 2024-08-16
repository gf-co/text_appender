import os
import tiktoken

def combine_books(books_directory, output_file, target_size_mb=32):
    target_size = target_size_mb * 1024 * 1024  # Convert MB to bytes
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        current_size = 0
        for filename in os.listdir(books_directory):
            if filename.endswith('.txt'):
                file_path = os.path.join(books_directory, filename)
                if current_size >= target_size:
                    break
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                    content = infile.read()
                    
                    # Find start and end markers
                    start_marker = "*** START OF THIS PROJECT GUTENBERG EBOOK ***"
                    end_marker = "*** END OF THIS PROJECT GUTENBERG EBOOK ***"
                    start_index = content.find(start_marker)
                    end_index = content.rfind(end_marker)
                    
                    # Extract content between markers, or use full content if markers not found
                    if start_index != -1 and end_index != -1:
                        book_content = content[start_index + len(start_marker):end_index]
                    else:
                        book_content = content
                    
                    # Write content
                    outfile.write(book_content.strip())
                    current_size = outfile.tell()
                    
                    if current_size < target_size:
                        outfile.write('\n\n' + '='*50 + '\n\n')  # Add separation between books
    
    actual_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Combined file created: {output_file}")
    print(f"File size: {actual_size_mb:.2f} MB")
    return output_file

def estimate_tokens_for_models(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    results = {}
    
    # Get all available encodings
    all_encodings = tiktoken.list_encoding_names()
    
    for encoding_name in all_encodings:
        try:
            enc = tiktoken.get_encoding(encoding_name)
            tokens = enc.encode(content)
            results[encoding_name] = len(tokens)
        except Exception as e:
            print(f"Error with encoding {encoding_name}: {str(e)}")
    
    return results

# Directory containing the books
books_directory = 'books'

output_file = 'combined_gutenberg_books_32mb.txt'
combined_file = combine_books(books_directory, output_file)

# Estimate tokens for different encodings
token_counts = estimate_tokens_for_models(combined_file)

print("\nToken count estimates for different encodings:")
for encoding, count in token_counts.items():
    print(f"{encoding}: {count} tokens")

# Updated embedding models pricing (standard API only)
# embedding_models = {
#     "text-embedding-3-small": 0.00002,  # $0.020 per 1M tokens
#     "text-embedding-3-large": 0.00013,  # $0.130 per 1M tokens
#     "text-embedding-ada-002": 0.0001    # $0.100 per 1M tokens
# }

# print("\nEstimated costs for embedding models:")
# for model, price_per_1m_tokens in embedding_models.items():
#     if "cl100k_base" in token_counts:  # Use cl100k_base for newer models
#         count = token_counts["cl100k_base"]
#     else:
#         print(f"Warning: cl100k_base encoding not found. Using first available encoding for {model}.")
#         count = next(iter(token_counts.values()))
#     estimated_cost = (count / 1_000_000) * price_per_1m_tokens
#     print(f"{model}: ${estimated_cost:.4f}")

# Print information about which encoding to use for specific models
print("\nRecommended encodings for specific models:")
model_encodings = {
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "text-davinci-002": "p50k_base",
    "text-davinci-003": "p50k_base",
    "davinci": "r50k_base"
}
for model, encoding in model_encodings.items():
    if encoding in token_counts:
        print(f"{model}: Use {encoding} encoding ({token_counts[encoding]} tokens)")
    else:
        print(f"{model}: Recommended encoding {encoding} not found in available encodings.")
