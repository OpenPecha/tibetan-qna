import json
import os


def parse_text_file(file_path):
    # Read the text file and split it into lines
    with open(file_path, encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    return lines


def combine_question_answer_files(directory):
    combined_data = []
    file_statistics = {}  # Dictionary to store the record count per file
    total_records = 0  # Total number of records across all files

    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith("_questions.txt"):
            question_file = filename
            base_filename = filename.replace("_questions.txt", "")
            answer_file = base_filename + "_answers.txt"

            # Check if corresponding answer file exists
            if os.path.exists(os.path.join(directory, answer_file)):
                # Parse the question and answer files
                questions = parse_text_file(os.path.join(directory, question_file))
                answers = parse_text_file(os.path.join(directory, answer_file))

                # Get the minimum number of questions and answers (just in case there's a mismatch)
                record_count = min(len(questions), len(answers))
                total_records += record_count

                # Store the record count for this file
                file_statistics[base_filename] = record_count

                # Combine question and answer pairs into dictionaries
                for i in range(record_count):
                    question = questions[i].split(" ", 1)[
                        -1
                    ]  # Remove indexing from question
                    answer = answers[i].split(" ", 1)[-1]  # Remove indexing from answer

                    qa_pair = {
                        "question": question,
                        "answer": answer,
                        "filename": base_filename,
                    }
                    combined_data.append(qa_pair)

    return combined_data, total_records, file_statistics


def save_to_json(data, output_file):
    # Save the combined data to a JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # Directory where the question and answer files are located
    directory = "data/output"  # Replace with your actual directory path

    # Combine question and answer files
    combined_data, total_records, file_statistics = combine_question_answer_files(
        directory
    )

    # Save the combined data to a JSON file
    output_file = "data/output/combined_qa.json"
    save_to_json(combined_data, output_file)

    # Print out statistics
    print(f"Total number of records: {total_records}")
    for filename, count in file_statistics.items():
        print(f"File: {filename}, Record count: {count}")

    print(f"Combined question-answer pairs have been saved to {output_file}")
