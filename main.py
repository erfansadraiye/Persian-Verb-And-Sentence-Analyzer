import re
from collections import defaultdict

from sentence_analyzer import analyze
from sentence_analyzer import split_sentences_semantically
from sentence_analyzer import convert_chunked_to_normal
from verb_scanner import find_verb_details

if __name__ == '__main__':
    text = 'من داشتم به پارک میرفتم. من داشتم می‌رفتم. من داشتم می‌رفتم.'

    sentences = split_sentences_semantically(text)
    sentences = [convert_chunked_to_normal(sentence) for sentence in sentences]

    seen_verbs = {}
    for sentence in sentences:
        extracted_info = analyze(sentence)
        spans_sentence = []
        for verb_parts in extracted_info["verbs_dependency_graph"]:
            verb = " ".join(verb_parts)

            if verb in seen_verbs:
                seen_verbs[verb] += 1
            else:
                seen_verbs[verb] = 0

            pattern = re.compile(verb)
            list_spans_verb = []
            for match in pattern.finditer(text):
                span = match.start(), match.start() + len(verb)
                list_spans_verb.append(span)

            span_current_verb = list_spans_verb[seen_verbs[verb]]
            spans_sentence.append(span_current_verb)

        subject = extracted_info["sub_dependency_graph"]
        list_subjects = ['من', 'تو', 'ما', 'شما', 'ایشان']
        if "".join(subject.split()) == 'آنها':
            subject = 'ایشان'
        if subject not in list_subjects:
            subject = 'او'

        details = find_verb_details(extracted_info["verbs_dependency_graph"], subject)
        print(details)
        print(spans_sentence)


