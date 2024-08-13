import customtkinter
import os
import threading
from tkinter import filedialog
from chatbot import query_rag  # Ensure this function is correctly imported
from saveEmbeddings import process_pdf  # Ensure this function is correctly imported

# Set appearance mode and theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Initialize main window
root = customtkinter.CTk()
root.geometry("800x500")  # Increase the size of the window
root.title("PDF Embeddings Generator")

# Create the main frame
frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# Define a font for better readability
custom_font = customtkinter.CTkFont(family="Helvetica", size=12)
bold_font = customtkinter.CTkFont(family="Helvetica", size=12, weight="bold")

# Define frames for different sections
embeddings_frame = customtkinter.CTkFrame(master=frame)
chat_frame = customtkinter.CTkFrame(master=frame)
menu_frame = customtkinter.CTkFrame(master=frame)  # Main menu frame

def show_embeddings_frame():
    chat_frame.grid_forget()
    menu_frame.grid_forget()
    embeddings_frame.grid(row=0, column=0, sticky='nsew')

def show_chat_frame():
    embeddings_frame.grid_forget()
    menu_frame.grid_forget()
    chat_frame.grid(row=0, column=0, sticky='nsew')

def show_main_menu():
    embeddings_frame.grid_forget()
    chat_frame.grid_forget()
    menu_frame.grid(row=0, column=0, sticky='nsew')

# Main Menu Buttons
embeddings_button = customtkinter.CTkButton(
    master=menu_frame,
    text="Generate Embeddings",
    command=show_embeddings_frame,
    font=custom_font
)
embeddings_button.pack(pady=20)

chat_button = customtkinter.CTkButton(
    master=menu_frame,
    text="Chat with Chatbot",
    command=show_chat_frame,
    font=custom_font
)
chat_button.pack(pady=20)

# ------------------
# Embeddings Frame UI
# ------------------
pdf_entry = customtkinter.CTkEntry(
    master=embeddings_frame,
    placeholder_text="Enter PDF file path",
    font=custom_font
)
pdf_entry.grid(row=0, column=0, columnspan=2, pady=12, padx=10, sticky='ew')

# Entry for the embeddings file path
embeddings_file_entry = customtkinter.CTkEntry(
    master=embeddings_frame,
    placeholder_text="Enter embeddings file path",
    font=custom_font
)
embeddings_file_entry.grid(row=1, column=0, columnspan=2, pady=12, padx=10, sticky='ew')

def browse_pdf():
    pdf_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf")],
        title="Select PDF File"
    )
    pdf_entry.delete(0, customtkinter.END)
    pdf_entry.insert(0, pdf_path)

browse_button = customtkinter.CTkButton(
    master=embeddings_frame,
    text="Browse PDF",
    command=browse_pdf,
    font=custom_font
)
browse_button.grid(row=2, column=0, pady=12, padx=(10, 5), sticky='w')

def generate_embeddings():
    pdf_path = pdf_entry.get().strip()
    if not pdf_path:
        update_result("Error: Please enter or select a PDF file.")
        return

    if not os.path.exists(pdf_path):
        update_result("Error: The selected file does not exist.")
        return

    def process_and_update():
        try:
            update_result("Processing the PDF and generating embeddings...")
            messages = process_pdf(pdf_path)  # Call the function from the external file
            for message in messages:
                update_result(message)
        except Exception as e:
            update_result(f"Error: {e}")

    threading.Thread(target=process_and_update, daemon=True).start()

generate_button = customtkinter.CTkButton(
    master=embeddings_frame,
    text="Generate Embeddings",
    command=generate_embeddings,
    font=custom_font,
    fg_color="red",  # Set the color of the button
    hover_color="darkred"
)
generate_button.grid(row=2, column=1, pady=12, padx=(5, 10), sticky='e')

result_textbox = customtkinter.CTkTextbox(
    master=embeddings_frame,
    width=750,
    height=200,
    wrap='word',
    state='disabled',
    font=custom_font
)
result_textbox.grid(row=3, column=0, columnspan=2, pady=12, padx=10, sticky='nsew')

def update_result(message):
    result_textbox.configure(state='normal')
    result_textbox.insert('end', message + '\n')
    result_textbox.configure(state='disabled')
    result_textbox.yview('end')

# Back Button for Embeddings Frame
back_button_embeddings = customtkinter.CTkButton(
    master=embeddings_frame,
    text="Back to Main Menu",
    command=show_main_menu,
    font=custom_font,
    fg_color="blue",  # Set the color of the button
    hover_color="darkblue"
)
back_button_embeddings.grid(row=4, column=0, pady=12, padx=10, sticky='sw')

# -------------------
# Chat Frame UI
# -------------------
# Back Button
back_button = customtkinter.CTkButton(
    master=chat_frame,
    text="Back to Main Menu",
    command=show_main_menu,
    font=custom_font,
    fg_color="blue",  # Set the color of the button
    hover_color="darkblue"
)
back_button.pack(pady=12, padx=10)

# Entry for the embeddings file path in chat frame
embeddings_file_chat_entry = customtkinter.CTkEntry(
    master=chat_frame,
    placeholder_text="Enter embeddings file path for chat",
    font=custom_font
)
embeddings_file_chat_entry.pack(pady=12, padx=10, fill='x')

def browse_embeddings_file():
    embeddings_file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")],
        title="Select Embeddings File"
    )
    formatted_path = format_file_path(embeddings_file_path)
    embeddings_file_chat_entry.delete(0, customtkinter.END)
    embeddings_file_chat_entry.insert(0, formatted_path)

def format_file_path(file_path: str) -> str:
    """Format the file path for Windows."""
    # Convert backslashes to forward slashes
    return file_path.replace('\\', '/')

browse_embeddings_button = customtkinter.CTkButton(
    master=chat_frame,
    text="Browse Embeddings File",
    command=browse_embeddings_file,
    font=custom_font
)
browse_embeddings_button.pack(pady=12, padx=10)

# Input field and button for the chat functionality
chat_entry = customtkinter.CTkEntry(
    master=chat_frame,
    placeholder_text="Enter your question here",
    font=custom_font
)
chat_entry.pack(pady=12, padx=10, fill='x')

response_counter = 1  # Initialize response counter

def send_query():
    global response_counter
    query_text = chat_entry.get().strip()
    embeddings_file_path = embeddings_file_chat_entry.get().strip()
    if not query_text:
        update_chat("Error: Please enter a query.")
        return

    if not embeddings_file_path or not os.path.exists(embeddings_file_path):
        update_chat("Error: Embeddings file path is invalid or file does not exist.")
        return

    def query_and_update():
        global response_counter
        response_text = query_rag(query_text, embeddings_file_path)  # Pass the file path to query_rag
        update_chat(f"Response {response_counter}:\n{response_text}")
        response_counter += 1

    threading.Thread(target=query_and_update, daemon=True).start()

send_button = customtkinter.CTkButton(
    master=chat_frame,
    text="Send",
    command=send_query,
    font=custom_font
)
send_button.pack(pady=12, padx=10)

# Textbox to show chat responses
chat_textbox = customtkinter.CTkTextbox(
    master=chat_frame,
    width=750,
    height=300,
    wrap='word',
    state='disabled',
    font=custom_font
)
chat_textbox.pack(pady=12, padx=10, fill='both', expand=True)

def update_chat(message):
    chat_textbox.configure(state='normal')
    chat_textbox.insert('end', message + '\n\n')  # Add two newline characters for spacing
    chat_textbox.configure(state='disabled')
    chat_textbox.yview('end')

# Initialize by showing the main menu
show_main_menu()

# Make sure that the grid expands properly
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

# Run the main loop
root.mainloop()
