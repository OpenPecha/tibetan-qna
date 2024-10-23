import re
from pathlib import Path
from typing import List

from docx import Document


class TibetanDocProcessor:
    TIBETAN_NUMBERS = "༠༡༢༣༤༥༦༧༨༩"

    def __init__(self):
        self.question_pattern = re.compile(
            r"༼\s*([༠-༩]+)\s*༽"
        )  # Capture Tibetan number inside '༼' and '༽'
        self.tseg_pattern = re.compile(r"་$")  # Check if the line ends with a tseg

    def process_docx(
        self, input_file: Path, output_question_file: Path, output_answer_file: Path
    ):
        document = Document(input_file)
        questions = []
        answers = []
        current_question = ""
        current_answer: List[str] = []
        question_counter = 1

        for para in document.paragraphs:
            line = para.text.strip()

            if not line:
                continue  # Skip empty lines

            match = self.question_pattern.search(line)
            if match:
                # If we find a new question marker and there is a current question, save it
                if current_question:
                    questions.append(f"{current_question.strip()}")
                    answers.append(
                        f"{self.int_to_tibetan(question_counter)}༽ "
                        + "\n".join(current_answer).strip()
                    )
                    current_question = ""
                    current_answer = []
                    question_counter += 1

                # Start a new question and remove the ༼ ༡ ༽ part
                current_question = line.replace(match.group(0), "").strip()
                current_question = (
                    f"{self.int_to_tibetan(question_counter)}༽ {current_question}"
                )
            elif current_question and self.tseg_pattern.search(current_question):
                # If the current question ends with a tseg, continue the question
                current_question += " " + line
            else:
                # It's an answer if there's no tseg at the end of the question
                current_answer.append(line)

        # Save the last question-answer pair
        if current_question:
            questions.append(f"{current_question.strip()}")
            answers.append(
                f"{self.int_to_tibetan(question_counter)}༽ "
                + "\n".join(current_answer).strip()
            )

        # Save questions and answers to their respective files
        self.save_to_file(output_question_file, questions)
        self.save_to_file(output_answer_file, answers)

    def int_to_tibetan(self, num: int) -> str:
        """Convert integer to Tibetan numeral."""
        tibetan_number = "".join(self.TIBETAN_NUMBERS[int(digit)] for digit in str(num))
        return tibetan_number

    def save_to_file(self, output_file: Path, data: list):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(data))


def main():
    processor = TibetanDocProcessor()

    input_file = Path("data/input/རྩོམ་རིག་ལོ་རྒྱུས་སྐོར་གྱི་དྲི་བ་དྲིས་ལན།.docx")
    base_name = input_file.stem
    output_dir = Path("data/output")
    output_question_file = output_dir / f"{base_name}_questions.txt"
    output_answer_file = output_dir / f"{base_name}_answers.txt"

    processor.process_docx(input_file, output_question_file, output_answer_file)


if __name__ == "__main__":
    main()
