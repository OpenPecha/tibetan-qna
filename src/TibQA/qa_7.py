import re
from pathlib import Path
from typing import List

from docx import Document

# Define a list of Tibetan numbers
tibetan_numbers = ["༠", "༡", "༢", "༣", "༤", "༥", "༦", "༧", "༨", "༩"]


class TibetanDocProcessor:
    def __init__(self, docx_file: Path):
        self.docx_file = Path(docx_file)
        self.questions: List[str] = []  # Annotate as a list of strings
        self.answers: List[str] = []  # Annotate as a list of strings

    def process(self):
        """Process the DOCX file to extract questions and answers."""
        doc = Document(self.docx_file)
        current_question: List[str] = []
        current_answer: List[str] = []
        is_question = False
        is_answer = False

        for para in doc.paragraphs:
            text = para.text.strip()

            if not text:
                continue

            # Check if it starts with an English number for the question
            if re.match(r"^\d+\.", text):  # Matches something like "1."
                # Append the previous question if one exists
                if current_question:
                    self.questions.append(" ".join(current_question).strip())
                    current_question = []

                # Start capturing the new question after the number
                current_question.append(text.split(".", 1)[1].strip())
                is_question = True
                is_answer = False

            # Check if it starts with "ལན།" for the answer
            elif text.startswith("ལན།"):
                # If there's an existing answer, append it
                if current_answer:
                    self.answers.append(" ".join(current_answer).strip())
                    current_answer = []

                # Start capturing the answer, marking it as an answer
                is_question = False
                is_answer = True
                current_answer.append(text.replace("ལན།", "").strip())

            elif is_question:
                # Continue adding to the current question
                current_question.append(text)

            elif is_answer:
                # Continue adding to the current answer
                current_answer.append(text)

        # Save the last question and answer
        if current_question:
            self.questions.append(" ".join(current_question).strip())
        if current_answer:
            self.answers.append(" ".join(current_answer).strip())

    def save_to_files(self, input_file, output_dir: str):
        """Save questions and answers to separate text files."""
        base_name = input_file.stem
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        questions_file = Path(output_dir) / f"{base_name}_questions.txt"
        answers_file = Path(output_dir) / f"{base_name}_answers.txt"

        # Save questions with Tibetan numbering
        with open(questions_file, "w", encoding="utf-8") as qf:
            for idx, question in enumerate(self.questions, start=1):
                tibetan_num = self.convert_to_tibetan_number(idx)
                qf.write(f"{tibetan_num}༽ {question}\n\n")

        # Save answers with Tibetan numbering
        with open(answers_file, "w", encoding="utf-8") as af:
            for idx, answer in enumerate(self.answers, start=1):
                tibetan_num = self.convert_to_tibetan_number(idx)
                af.write(f"{tibetan_num}༽ {answer}\n\n")

        print(f"Questions saved to {questions_file}")
        print(f"Answers saved to {answers_file}")

    def convert_to_tibetan_number(self, num):
        """Convert an integer to Tibetan numerals."""
        tibetan_num = ""
        for digit in str(num):
            tibetan_num += tibetan_numbers[int(digit)]
        return tibetan_num


def main():
    # Path to your input DOCX file and the output directory
    input_file = Path("data/input/གསོ་བ་རིག་པའི་སྐོར་གྱི་དྲི་བ་དྲིས་ལན་འོས་སྦྱོར།.docx")
    output_dir = "data/output"

    # Initialize and process the document
    processor = TibetanDocProcessor(input_file)
    processor.process()

    # Save questions and answers to text files
    processor.save_to_files(input_file, output_dir)


if __name__ == "__main__":
    main()
