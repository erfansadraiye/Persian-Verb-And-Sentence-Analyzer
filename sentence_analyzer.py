from hazm import *
import re

from nltk import tree2conlltags

tagger = POSTagger(model='pos_tagger.model')
lemmatizer = Lemmatizer()

'''
Returns a list of POS tagged sub_sentences, each of which is a str object.
If the sentences is not a compound of multiple sentences, the list will have one element.
'''
def chunk_sentence(sentence):
    tagged = tagger.tag(word_tokenize(sentence))
    print(tagged)
    chunker = Chunker(model='chunker.model')
    tree = chunker.parse(tagged)
    chunked = tree2brackets(tree)
    separator_pattern = re.compile(r'] ([^\[ ]+?) \[')
    separators = separator_pattern.findall(chunked)
    non_punctuation_tokens = set(map(lambda e: e[0] if e[1] != 'PUNCT' else None, tagged))
    conjunctions = non_punctuation_tokens.intersection(separators)
    sub_sentences = [[]]
    for tag in tagged:
        if tag[0] in conjunctions:
            sub_sentences.append([])
        else:
            sub_sentences[-1].append(tag)

    chunked_sub_sentences = [tree2brackets(chunker.parse(sub_sentence)) for sub_sentence in sub_sentences]
    return chunked_sub_sentences

def clean_verb(verb_phase):
    return re.subn('\u200c|_', ' ', verb_phase)[0]
def extract_verb_phrases(chunked):
    verb_phrase_pattern = re.compile(r'\[([^\[]+?) VP]')
    verb_phrases = verb_phrase_pattern.findall(chunked)
    if verb_phrases:
        verb_phrases = [clean_verb(vp) for vp in  verb_phrases] # replace `nim fasele` to space!

        for verb_phrase in verb_phrases:
            print("VERB:", verb_phrase)
    return verb_phrases


def extract_objects(chunked):
    obj_pattern = re.compile(r'\[([^\[]+) NP] \[را POSTP]')
    objects = obj_pattern.findall(chunked)
    for object in objects:
        print("OBJ:", object)
    return objects


def create_dependency_graph(sentence):
    print("Dependency Parser\n", sentence)
    parser = DependencyParser(tagger=tagger, lemmatizer=lemmatizer)
    dependencyGraph = parser.parse(word_tokenize(sentence))
    verbs = []
    obj_parts = []
    subj_parts = []
    for i in range(len(dependencyGraph.nodes)):
        info = dependencyGraph.nodes[i]
        print(info['word'], '-> rel:', info['rel'], ', tag:', info['tag'])
        if info['tag'] == 'VERB':
            verb_parts = []
            if info['deps']:
                for type in info['deps']:
                    if type == 'compound':
                        for index in info['deps'][type]:
                            verb_parts.append(dependencyGraph.nodes[index]['word'])
            verb_parts.append(clean_verb(info['word']))
            print(verb_parts)
            verbs.append(verb_parts)
        if info['rel'] == 'obj':
            if info['deps']:  # if had dependencies
                for type in info['deps']:
                    if type != "case":  # ignore را
                        for index in info['deps'][type]:
                            obj_parts.append((index, dependencyGraph.nodes[index]["word"]))
            obj_parts.append((info['address'], info['word']))
            obj_parts.sort(key=lambda a: a[0])
            obj = " ".join([obj_part[1] for obj_part in obj_parts])
            print("OBJ:", obj)
        if info['rel'] == 'nsubj':
            if info['deps']: # if had dependencies
                for type in info['deps']:
                    for index in info['deps'][type]:
                        subj_parts.append((index, dependencyGraph.nodes[index]["word"]))
            subj_parts.append((info['address'], info['word']))
            subj_parts.sort(key=lambda a: a[0])
            subj = " ".join([subj_part[1] for subj_part in subj_parts])
            print("SUB:", subj)
    print(dependencyGraph)
    return (subj, obj, verb_parts)

def remove_brackets(chunked_sent):
    return re.subn('_', ' ', re.subn(r'\[|]|[A-Z]', '', chunked_sent)[0])[0]

def main():
    normalizer = Normalizer()
    # text = input()
    text = "این کتاب احساسات من را بر می‌انگیزد. من اشتباهم را جبران کردم. صحبت‌های او من را بر آشفت!"
    sentences = sent_tokenize(text)
    for sentence in sentences:
        normalized_sentence = normalizer.normalize(sentence)
        print(normalized_sentence)
        chunked_sub_sentences = chunk_sentence(normalized_sentence)
        for chunked_sub_sentence in chunked_sub_sentences:
            print(chunked_sub_sentence)
            objs = extract_objects(chunked_sub_sentence)
            verbs = extract_verb_phrases(chunked_sub_sentence)
            print("### ### ### ### ### ### ### ")
            subj, obj, verbs = create_dependency_graph(remove_brackets(chunked_sub_sentence))
        print("************************************************************************")


if __name__ == "__main__":
    main()
