import re
from pathlib import Path

import docx


def convert_to_tibetan_number(n):
    """Convert Arabic numerals to Tibetan numerals"""
    tibetan_digits = ["༠", "༡", "༢", "༣", "༤", "༥", "༦", "༧", "༨", "༩"]
    return "".join(tibetan_digits[int(d)] for d in str(n)) + "༽"


def clean_tibetan_text(text):
    """Clean Tibetan text by removing extra spaces while preserving punctuation"""
    text = re.sub(r"\s+", " ", text.strip())
    return text


def extract_qa_from_docx(docx_path, questions_output, answers_output):
    """
    Extract questions and answers from a Tibetan docx file, re-index them, and save to separate text files.
    """
    try:
        # Read the docx file
        doc = docx.Document(docx_path)

        # Combine all paragraphs into one text
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs)

        # Debug: Print first part of the text
        print("\nDebug: First 200 characters of text:")
        print(full_text[:200])

        # Pattern to match the full Q&A pairs but ignore existing numbering
        qa_pattern = r"དྲི་བ།\s*(.*?)\s*ལན།\s*(.*?)(?=དྲི་བ།|$)"

        # Find all Q&A pairs
        qa_pairs = re.findall(qa_pattern, full_text, re.DOTALL)
        print(f"\nDebug: Found {len(qa_pairs)} Q&A pairs")

        # Create output directory if it doesn't exist
        output_dir = Path(questions_output).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Prepare questions and answers lists with re-indexed Tibetan numerals
        questions = []
        answers = []

        for i, (question, answer) in enumerate(qa_pairs, 1):
            # Convert the index to a Tibetan numeral
            tibetan_index = convert_to_tibetan_number(i)

            # Clean the question and answer text
            cleaned_question = clean_tibetan_text(question)
            cleaned_answer = clean_tibetan_text(answer)

            question_entry = f"{tibetan_index} {cleaned_question}\n\n"
            answer_entry = f"{tibetan_index} {cleaned_answer}\n\n"

            questions.append(question_entry)
            answers.append(answer_entry)

        # Write questions to file
        with open(questions_output, "w", encoding="utf-8") as f:
            f.writelines(questions)

        # Write answers to file
        with open(answers_output, "w", encoding="utf-8") as f:
            f.writelines(answers)

        print(f"\nSuccessfully processed {len(qa_pairs)} question-answer pairs.")
        print(f"Questions saved to: {questions_output}")
        print(f"Answers saved to: {answers_output}")

        if qa_pairs:
            print("\nFirst Q&A pair for verification:")
            print(f"Question: {questions[0].strip()}")
            print(f"Answer: {answers[0].strip()}")

        return len(qa_pairs)

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        import traceback

        traceback.print_exc()
        return 0


def main():
    # Get current working directory
    current_dir = Path.cwd()

    # Configure paths
    input_file = current_dir / "data" / "input" / "དྲི་ལན་སྣ་ཚོགས།.docx"
    output_dir = current_dir / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create output filenames
    base_name = input_file.stem
    questions_file = output_dir / f"{base_name}_questions.txt"
    answers_file = output_dir / f"{base_name}_answers.txt"

    try:
        print(f"\nProcessing file: {input_file}")
        print(f"File exists: {input_file.exists()}")

        # Process the document
        pairs_count = extract_qa_from_docx(
            str(input_file), str(questions_file), str(answers_file)
        )

        if pairs_count > 0:
            print("\nExtraction completed successfully!")
        else:
            print(
                "\nNo question-answer pairs were extracted. Please check the input file format."
            )

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
