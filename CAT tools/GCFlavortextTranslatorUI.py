import os
import tkinter as tk
from tkinter import filedialog
from lxml import etree
import openai
from langdetect import detect

# Set your OpenAI API key
openai.api_key = "put your open AI key here."

# Open a directory selection dialog
root = tk.Tk()
root.withdraw()

selected_directory = filedialog.askdirectory(title="Select a directory containing the XML files")

if not selected_directory:
    print("No directory selected. Exiting.")
    exit()

def get_target_language_from_directory(directory):
    return os.path.basename(directory)

def is_file_read_only(file_path):
    return not os.access(file_path, os.W_OK)

def rewrite_text_in_language(prompt, language):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error rewriting text: {e}")
        return None

def process_files_in_directory(directory, language):
    for subdir, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(subdir, file)
            
            # Check if the file is read-only
            if is_file_read_only(file_path):
                continue

            print(f"Processing file: {file_path}")

            try:
                tree = etree.parse(file_path)
                root = tree.getroot()

                for text_element in root.findall(".//String"):
                    original_text = text_element.text

                    # Check if text is in English
                    detected_lang = detect(original_text)
                    if detected_lang == "en":
                        prompt = f"Rewrite the following text as {language} in the style of a {language} Sci-Fi author while being succinct to ensure you are accurately conveying the original meaning. Only rewrite what you are given in {language}. Do not translate anything that is in any type of bracket. If you can't rewrite something then don't change anything. Do not output anything other than the text rewritten in {language}: {original_text}"
                        rewritten_text = rewrite_text_in_language(prompt, language)
                        if rewritten_text:
                            text_element.text = rewritten_text
                            print(f"Rewritten Text: {rewritten_text}")

                # Save the updated content back to the original file
                tree.write(file_path, encoding='utf-8', xml_declaration=True)
            except Exception as e:
                print(f"Error processing file {file_path}. Error: {e}")

def main():
    language = get_target_language_from_directory(selected_directory)
    process_files_in_directory(selected_directory, language)

if __name__ == '__main__':
    main()
