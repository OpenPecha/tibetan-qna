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
        # Pattern to match Tibetan numbers at the start of a line (e.g., ༡ ༢ ༣)
        self.question_number_pattern = re.compile(r"^[༠-༩]+\s*")
        self.answer_prefix = "ལན།"
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

    def int_to_tibetan_numeral(self, num: int) -> str:
        """Convert integer to Tibetan numeral string."""
        try:
            return "".join(
                TibetanTextProcessor.TIBETAN_DIGITS[int(d)] for d in str(num)
            )
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to convert number {num} to Tibetan numeral: {e}")

    def clean_question_text(self, text: str) -> str:
        """Clean the question text by removing unwanted numbers."""
        # Remove Tibetan numbers at the beginning of the question
        text = self.question_number_pattern.sub("", text).strip()
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
        current_question = ""
        current_answer: List[str] = []
        is_answer = False
        question_counter = 1  # Counter to keep track of question/answer pairs

        for paragraph in document.paragraphs:
            line = paragraph.text.strip()

            # If line is empty, skip it
            if not line:
                continue

            # Check if the line starts with a Tibetan number (potential question)
            if self.question_number_pattern.match(line):
                # If we were processing a question, save it along with its answer
                if current_question and current_answer:
                    parsed_questions.append(
                        f"{self.int_to_tibetan_numeral(question_counter)}༽ {self.clean_question_text(current_question)}"
                    )
                    parsed_answers.append(
                        f"{self.int_to_tibetan_numeral(question_counter)}༽ "
                        + "\n".join(current_answer)
                    )
                    current_question = ""
                    current_answer = []
                    question_counter += 1

                # Start processing a new question
                current_question = line
                is_answer = False  # Reset to false as we are starting a new question
            elif line.startswith(self.answer_prefix):
                # If the line starts with 'ལན།', it's an answer line
                is_answer = True
                current_answer.append(line[len(self.answer_prefix) :].strip())  # noqa
            elif is_answer:
                # If we're already in the answer block, continue appending lines
                current_answer.append(line)
            else:
                # Append to current question if it's not part of an answer
                current_question += f" {line}"

        # Process the last question-answer pair
        if current_question and current_answer:
            parsed_questions.append(
                f"{self.int_to_tibetan_numeral(question_counter)}༽ {self.clean_question_text(current_question)}"
            )
            parsed_answers.append(
                f"{self.int_to_tibetan_numeral(question_counter)}༽ "
                + "\n".join(current_answer)
            )

        self.logger.info(f"Parsed {len(parsed_questions)} question-answer pairs")
        return parsed_questions, parsed_answers

    def save_output(
        self,
        input_file: Path,
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
    input_file = Path("data/input/ལེགས་སྦྱར་དྲི་བ་དྲིས་ལན།.docx")
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
