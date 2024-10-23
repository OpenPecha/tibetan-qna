import logging
import os
import re
from typing import List, Tuple

from docx import Document


class TibetanTextProcessor:
    """Process Tibetan text documents with questions and answers."""

    def __init__(self, debug=True):
        # Regular expressions to match the start of a question and answer
        self.question_start_pattern = re.compile(r"^༈")  # Questions start with "༈"
        self.answer_start_pattern = re.compile(
            r"^(དེའི་ལན་ནི།|དེའི་དོན་ནི།)"
        )  # Answers start with these patterns
        self.answer_remove_pattern = re.compile(
            r"^(དེའི་ལན་ནི།|དེའི་དོན་ནི།)"
        )  # For removing unwanted phrases in the answers
        self.shey_character = (
            "།"  # The "shey" character, used as a delimiter in Tibetan
        )
        self.debug = debug

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for the processor."""
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def clean_question_text(self, text: str) -> str:
        """Clean the question text by removing everything before the first shey character."""
        # Remove everything before the first "།" (shey) character
        if self.shey_character in text:
            return text.split(self.shey_character, 1)[1].strip()
        return text.strip()

    def clean_answer_text(self, text: str) -> str:
        """Clean the answer text by removing unwanted prefixes."""
        # Remove the unwanted answer prefixes such as "དེའི་ལན་ནི།" or "དེའི་དོན་ནི།"
        return self.answer_remove_pattern.sub("", text).strip()

    def parse_docx(self, file_path: str) -> Tuple[List[str], List[str]]:
        """Parse questions and answers from a .docx file."""
        try:
            self.logger.info(f"Starting to parse document: {file_path}")
            document = Document(file_path)
        except Exception as e:
            self.logger.error(f"Failed to open document {file_path}: {e}")
            raise

        parsed_questions: List[str] = []
        parsed_answers: List[str] = []
        current_question = None
        current_answer: List[str] = []
        question_counter = 1

        for paragraph in document.paragraphs:
            line = paragraph.text.strip()
            if not line:
                continue

            # Check if the line starts with a question (starting with "༈")
            if self.question_start_pattern.match(line):
                self.logger.debug(f"Found question: {line}")
                if current_question:
                    self._process_current_qa(
                        current_question,
                        current_answer,
                        question_counter,
                        parsed_questions,
                        parsed_answers,
                    )
                    question_counter += 1
                # Clean the question by removing everything before the first "།"
                current_question = self.clean_question_text(line)
                current_answer = []
            # Check if the line starts with an answer (starting with "དེའི་ལན་ནི།" or "དེའི་དོན་ནི།")
            elif self.answer_start_pattern.match(line):
                current_answer.append(self.clean_answer_text(line))  # Clean answer text
            else:
                # Continue building the answer
                current_answer.append(line)
                self.logger.debug(f"Added to current answer: {line}")

        # Process the last question-answer pair
        if current_question:
            self._process_current_qa(
                current_question,
                current_answer,
                question_counter,
                parsed_questions,
                parsed_answers,
            )

        self.logger.info(f"Parsed {len(parsed_questions)} question-answer pairs")
        return parsed_questions, parsed_answers

    def _process_current_qa(
        self,
        question: str,
        answer_lines: List[str],
        counter: int,
        questions_list: List[str],
        answers_list: List[str],
    ) -> None:
        """Process a single question-answer pair."""
        # Add new question number in the desired format
        numbered_question = f"{counter}༽ {question}"
        questions_list.append(numbered_question)

        # Clean and join answer lines
        cleaned_answer = "\n".join(answer_lines)

        # Add new answer number
        numbered_answer = f"{counter}༽ {cleaned_answer}"
        answers_list.append(numbered_answer)

    def save_output(
        self,
        input_file,
        questions: List[str],
        answers: List[str],
        output_dir: str,
    ) -> None:
        """Save processed questions and answers to files."""
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_path = os.path.join(output_dir)
        os.makedirs(output_path, exist_ok=True)

        questions_path = os.path.join(output_path, f"{base_name}_questions.txt")
        answers_path = os.path.join(output_path, f"{base_name}_answers.txt")

        try:
            # Save questions with double newlines for better formatting
            with open(questions_path, "w", encoding="utf-8") as qf:
                qf.write("\n\n".join(questions))

            # Save answers with double newlines for better formatting
            with open(answers_path, "w", encoding="utf-8") as af:
                af.write("\n\n".join(answers))

            self.logger.info(
                f"Successfully saved output files:\n"  # noqa
                f"Questions: {questions_path}\n"
                f"Answers: {answers_path}"
            )

        except Exception as e:
            self.logger.error(f"Failed to save output files: {e}")
            raise


def main():
    # Input and output paths
    input_file = "data/input/གཞན་སྟོང་བགྲོ་གླེང་ཐེངས་དང་པོའི་དྲི་བ་དྲིས་ལན། 10.docx"
    output_dir = "data/output"

    # Initialize processor with debug mode
    processor = TibetanTextProcessor(debug=True)

    try:
        # Parse document
        questions, answers = processor.parse_docx(input_file)

        # Save results
        processor.save_output(input_file, questions, answers, output_dir)

    except Exception as e:
        logging.error(f"Processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
