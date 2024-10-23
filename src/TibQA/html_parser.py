from bs4 import BeautifulSoup


# Function to convert an integer to Tibetan-style numbering
def get_tibetan_number(index):
    tibetan_digits = ["༠", "༡", "༢", "༣", "༤", "༥", "༦", "༧", "༨", "༩"]
    tibetan_number = ""

    # Convert the index into a Tibetan-style number
    for digit in str(index):
        tibetan_number += tibetan_digits[int(digit)]

    return tibetan_number + "༽"


def parse_html(file_path):
    # Open the HTML file and read its contents
    with open(file_path, encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    questions = []
    answers = []

    question_index = 1
    answer_index = 1

    # Find all paragraphs containing spans with class 'span0'
    paragraphs = soup.find_all("p")

    for paragraph in paragraphs:
        span = paragraph.find("span", class_="span0")
        if span:
            content = span.get_text().strip()

            # Check if the paragraph contains 'ལན།', marking it as an answer
            if "ལན།" in content:
                # Remove 'ལན།' from the answer and apply Tibetan indexing
                answer = content.replace("ལན།", "").strip()
                indexed_answer = f"{get_tibetan_number(answer_index)} {answer}"
                answers.append(indexed_answer)
                answer_index += 1
            else:
                # If it's a question, extract the content after the first space and add Tibetan indexing
                question = content.split(" ", 1)[-1] if " " in content else content
                indexed_question = f"{get_tibetan_number(question_index)} {question}"
                questions.append(indexed_question)
                question_index += 1

    return questions, answers


def save_to_file(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        for item in data:
            file.write(item + "\n")


if __name__ == "__main__":
    # Path to the input HTML file
    input_file = "data/input/སྒྲུང་གཏམ་གསར་རྩོམ་ཐད་ཀྱི་དྲི་བ་དྲིས་ལན།༼ཆ་ཚང་།༽.html"  # Replace with your HTML file path

    # Parse the HTML to extract questions and answers
    questions, answers = parse_html(input_file)

    # Save the questions and answers to separate text files
    save_to_file(
        "data/output/སྒྲུང་གཏམ་གསར་རྩོམ་ཐད་ཀྱི་དྲི་བ་དྲིས་ལན།༼ཆ་ཚང་།༽_questions.txt",
        questions,
    )
    save_to_file(
        "data/output/སྒྲུང་གཏམ་གསར་རྩོམ་ཐད་ཀྱི་དྲི་བ་དྲིས་ལན།༼ཆ་ཚང་།༽_answers.txt",
        answers,
    )
