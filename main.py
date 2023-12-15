from sentence_analyzer import analyze
from sentence_analyzer import split_sentences_semantically
from verb_scanner import find_verb_details

if __name__ == '__main__':
    text = 'من کتابم را به کتابخانه خواهم برد.'
    extracted_info = sentence_analyzer.analyze(text)
    for key in extracted_info:
        print(key, extracted_info[key])

    subject = "hahaha"
    list_subjects = ['من', 'تو', 'ما', 'شما', 'ایشان']
    if "".join(subject.split()) == 'آنها':
        subject = 'ایشان'
    if subject not in list_subjects:
        subject = 'او'
    details = find_verb_details(extracted_info["verbs_dependency_graph"], subject)
    sentences = split_sentences_semantically(text)
    extracted_info = analyze(text)
    # for key in extracted_info:
    #     print(key, extracted_info[key])
    details = find_verb_details(extracted_info["verbs_dependency_graph"])
    for detail in details:
        print(detail)
