import logging
import re
from pathlib import Path
from typing import List, Tuple

from docx import Document


class TibetanTextProcessor:
    """Process Tibetan text documents with questions and answers identified by Tibetan alphabet markers."""

    def __init__(self, debug=True):
        self.debug = debug
        # This pattern detects Tibetan alphabet markers (e.g., ཀ, ཁ, ག, etc.)
        self.alphabet_pattern = re.compile(r"^[ཀ-ཨ]\s*$")
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for the processor."""
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

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
        current_question: List[str] = []
        current_answer: List[str] = []
        question_counter = 1

        for paragraph in document.paragraphs:
            line = paragraph.text.strip()
            if not line:
                continue

            if self.alphabet_pattern.match(
                line
            ):  # If the line is a Tibetan alphabet marker, it's a new question
                if current_question or current_answer:
                    self._process_current_qa(
                        current_question,
                        current_answer,
                        question_counter,
                        parsed_questions,
                        parsed_answers,
                    )
                    question_counter += 1
                    current_question = []
                    current_answer = []
                current_question.append(line)  # This is part of the question

            elif (
                current_question
            ):  # Collect the text after the Tibetan alphabet marker as part of the question
                if len(current_question) == 1:
                    current_question.append(line)
                else:
                    current_answer.append(line)

        # Ensure the last question-answer pair is processed
        if current_question or current_answer:
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
        question: List[str],
        answer: List[str],
        counter: int,
        questions_list: List[str],
        answers_list: List[str],
    ) -> None:
        """Process a single question-answer pair."""
        # Remove Tibetan alphabet marker from the question
        cleaned_question = " ".join(question).strip()
        cleaned_question = re.sub(
            r"^[ཀ-ཨ]\s*", "", cleaned_question
        ).strip()  # Remove the Tibetan alphabet marker

        # Add new question number without Tibetan alphabet marker
        numbered_question = f"{counter}༽ {cleaned_question}"
        questions_list.append(numbered_question)

        # Clean answer and join into one string
        numbered_answer = f"{counter}༽ " + " ".join(answer).strip()
        answers_list.append(numbered_answer)

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
            # Save questions
            with open(questions_path, "w", encoding="utf-8") as qf:
                qf.write("\n\n".join(questions))

            # Save answers
            with open(answers_path, "w", encoding="utf-8") as af:
                af.write("\n\n".join(answers))

            self.logger.info(
                f"Successfully saved output files:\nQuestions: {questions_path}\nAnswers: {answers_path}"  # noqa
            )
            return questions_path, answers_path

        except Exception as e:
            self.logger.error(f"Failed to save output files: {e}")
            raise


def main():
    input_file = Path(
        "data/input/ཐོན་མིའི་ཞལ་ལུང་གི་ཨེ་ཁྱབ་སུམ་ཅུའི་དྲི་བ་དྲིས་ལན། 11 (1).docx"
    )
    output_dir = "data/output"

    processor = TibetanTextProcessor(debug=True)

    try:
        questions, answers = processor.parse_docx(input_file)
        processor.save_output(input_file, questions, answers, output_dir)
    except Exception as e:
        logging.error(f"Processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
