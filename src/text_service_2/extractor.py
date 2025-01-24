import re


def extract(text):
    lines = text.splitlines()

    paragraphs = []
    paragraph = []

    for line in lines:
        line = line.strip()

        if line == "":
            p = re.split(
                r"([a-zA-Z\)]{3}\.)\s([a-zA-Z]{1})",
                " ".join(paragraph)
            )

            p1 = p[0:2]
            p2 = p[2:]

            p_tmp = []

            p_first_part = "".join(p1)
            if len(p_first_part):
                p_tmp.append(p_first_part)

            for i in range(0, len(p2), 3):
                p_part = "".join(p2[i:i+3])

                if len(p_part):
                    p_tmp.append(p_part)

            p = p_tmp

            if len(p):
                paragraphs.append(p)

            paragraph = []
        else:
            has_space = " " in line
            has_length = len(line) >= 5

            if has_length or has_space:
                paragraph.append(line)

    sentences = []
    for paragraph in paragraphs:
        sentences += paragraph

    paragraphs = [" ".join(p) for p in paragraphs]

    pages = []
    for page in text.split("\f"):
        if page.strip() != "":
            pages.append(page)

    return sentences, paragraphs, pages
