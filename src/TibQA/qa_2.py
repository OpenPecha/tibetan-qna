import logging
import re
from pathlib import Path
from typing import List, Tuple

from docx import Document


class TibetanTextProcessor:
    """Process Tibetan text documents with questions and answers."""

    # Tibetan digits mapping for conversion
    TIBETAN_DIGITS = "༠༡༢༣༤༥༦༧༨༩"

    def __init__(self, debug=True):
        # Compile regex patterns once during initialization
        # Updated pattern to match Tibetan numbers at the start of a line
        self.initial_number_pattern = re.compile(r"^[༠-༩]+")
        # Pattern to match the format "༡༽ ༡" and similar
        self.duplicate_number_pattern = re.compile(r"༽\s*[༠-༩]+\s*")
        self.answer_prefix = "ལན། "
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

    @staticmethod
    def int_to_tibetan_numeral(num: int) -> str:
        """Convert integer to Tibetan numeral string."""
        try:
            return "".join(
                TibetanTextProcessor.TIBETAN_DIGITS[int(d)] for d in str(num)
            )
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert number {num} to Tibetan numeral: {e}")

    def clean_question_text(self, text: str) -> str:
        """Clean the question text by removing unwanted numbers."""
        # First remove any initial Tibetan numbers
        text = self.initial_number_pattern.sub("", text).strip()
        # Then remove any numbers after the ༽ symbol
        text = self.duplicate_number_pattern.sub("༽ ", text).strip()
        return text

    def parse_docx(self, file_path: Path) -> Tuple[List[str], List[str]]:
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

            # Check if the line starts with a Tibetan numeral
            if self.initial_number_pattern.match(line):
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
                current_question = line
                current_answer = []
            else:
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
        # Clean question text by removing unwanted numbers
        cleaned_question = self.clean_question_text(question)

        # Add new question number in the desired format
        numbered_question = (
            f"{self.int_to_tibetan_numeral(counter)}༽ {cleaned_question}"
        )
        questions_list.append(numbered_question)

        # Clean and join answer lines
        cleaned_answer = []
        for line in answer_lines:
            if line.startswith(self.answer_prefix):
                line = line[len(self.answer_prefix) :]  # noqa
            cleaned_answer.append(line)

        # Add new answer number
        numbered_answer = f"{self.int_to_tibetan_numeral(counter)}༽ " + "\n".join(
            cleaned_answer
        )
        answers_list.append(numbered_answer)

    def save_output(
        self,
        input_file,
        questions: List[str],
        answers: List[str],
        output_dir: str,
    ) -> Tuple[Path, Path]:
        """Save processed questions and answers to files."""
        base_name = input_file.stem
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        questions_path = output_path / f"{base_name}_questions.txt"
        answers_path = output_path / f"{base_name}_answers.txt"

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

            return questions_path, answers_path

        except Exception as e:
            self.logger.error(f"Failed to save output files: {e}")
            raise


def main():
    # Input and output paths
    input_file = Path(
        "data/input/གསོ་བ་རིག་པའི་སྐོར་གྱི་དྲི་བ་དྲིས་ལན་འོས་སྦྱོར།(1).docx"
    )
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
