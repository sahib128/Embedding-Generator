import json
import os
from embeddings import get_embeddings
from processingTxt import split_chunks  # Adjust the import according to your module

# Define the file to store processed document information
PROCESSED_DOCS_FILE = 'processed_docs.json'

def load_processed_docs():
    """
    Load the list of processed documents from the file.
    """
    if os.path.exists(PROCESSED_DOCS_FILE):
        with open(PROCESSED_DOCS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                print(f"JSON decode error while loading processed docs: {e}")
                return {}
    return {}

def save_processed_docs(processed_docs):
    """
    Save the list of processed documents to the file.
    """
    try:
        with open(PROCESSED_DOCS_FILE, 'w') as file:
            json.dump(processed_docs, file, indent=4)
    except IOError as e:
        print(f"An error occurred while saving the processed docs: {e}")

def get_embeddings_for_chunks(chunks):
    """
    Generate embeddings for chunks of the PDF.
    """
    embeddings = []
    for chunk in chunks:
        try:
            embedding = get_embeddings(chunk.page_content)  # Access page_content of Chunk
            embeddings.append({
                'chunk_id': chunk.metadata.get('id', 'unknown_id'),  # Use metadata ID for unique identification
                'chunk': chunk.page_content,
                'embedding': embedding.tolist()  # Convert numpy array to list for JSON serialization
            })
        except Exception as e:
            print(f"Error while generating embedding for chunk: {e}")
            embeddings.append({
                'chunk_id': chunk.metadata.get('id', 'unknown_id'),
                'chunk': chunk.page_content,
                'embedding': None
            })
    return embeddings

def save_embeddings_to_file(embeddings, file_path):
    """
    Save embeddings to a JSON file.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(embeddings, file, indent=4)
        return f"Embeddings saved to {file_path}"
    except IOError as e:
        return f"An error occurred while saving the file: {e}"

def process_pdf(pdf_path, embeddings_dir='embeddings'):
    """
    Process the PDF to generate embeddings and save them to a file.
    """
    messages = []
    processed_docs = load_processed_docs()
    pdf_path = os.path.abspath(pdf_path)  # Use absolute path for consistent comparison

    # Check if the document has already been processed
    if pdf_path in processed_docs:
        messages.append(f"Embeddings for document already exist at {processed_docs[pdf_path]}.")
        return messages

    # Ensure the embeddings directory exists
    if not os.path.exists(embeddings_dir):
        os.makedirs(embeddings_dir)
        messages.append(f"Created directory: {embeddings_dir}")

    output_file_path = os.path.join(embeddings_dir, f'{os.path.basename(pdf_path)}_embeddings.json')

    try:
        # Split the PDF into chunks
        chunks = split_chunks(pdf_path)

        # Debugging information
        messages.append(f"Type of chunks: {type(chunks)}")
        messages.append(f"Number of chunks: {len(chunks)}")
        if chunks:
            messages.append(f"First chunk ID: {chunks[0].metadata.get('id', 'unknown_id')}")

        # Get embeddings for the chunks
        embeddings = get_embeddings_for_chunks(chunks)

        # Save embeddings to a file
        save_message = save_embeddings_to_file(embeddings, output_file_path)
        messages.append(save_message)

        # Update the list of processed documents
        processed_docs[pdf_path] = output_file_path
        save_processed_docs(processed_docs)
    except Exception as e:
        messages.append(f"An error occurred: {e}")

    return messages
