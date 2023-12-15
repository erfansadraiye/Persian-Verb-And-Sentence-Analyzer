from hazm import *
import re

tagger = POSTagger(model='pos_tagger.model')
lemmatizer = Lemmatizer()


'''
Returns a list of POS tagged sub_sentences, each of which is a str object.
If the sentences is not a compound of multiple sentences, the list will have one element.
'''
def chunk_sentence(sentence):
    tagged = tagger.tag(word_tokenize(sentence))
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
            # add new list for new sentence
            sub_sentences.append([])
        else:
            # current sentence is not finished
            sub_sentences[-1].append(tag)
    chunked_sub_sentences = [tree2brackets(chunker.parse(sub_sentence)) for sub_sentence in sub_sentences]
    return chunked_sub_sentences


def clean_verb(verb_phase):
    return re.subn('\u200c|_', ' ', verb_phase)[0]


def extract_verb_phrases(chunked):
    verb_phrase_pattern = re.compile(r'\[([^\[]+?) VP]')
    verb_phrases = verb_phrase_pattern.findall(chunked)
    if verb_phrases:
        verb_phrases = [clean_verb(vp) for vp in verb_phrases]
    return verb_phrases


def extract_objects(chunked):
    obj_pattern = re.compile(r'\[([^\[]+) NP] \[را POSTP]')
    objects = obj_pattern.findall(chunked)
    return objects


'''
Receives a node from dependency graph and prints its word, part os speech tag, and rel. 
'''
def print_tagged_word(info):
    print(info['word'], '-> rel:', info['rel'], ', tag:', info['tag'])


def extract_subj_from_dependency_graph(dependencyGraph, info):
    subj_parts = []
    if info['deps']:  # if had dependencies
        for type in info['deps']:
            for index in info['deps'][type]:
                subj_parts.append((index, dependencyGraph.nodes[index]["word"]))
    subj_parts.append((info['address'], info['word']))
    subj_parts.sort(key=lambda a: a[0])
    if subj_parts:
        subj = " ".join([subj_part[1] for subj_part in subj_parts])
    else:
        subj = None
    return subj


def extract_obj_from_dependency_graph(dependencyGraph, info):
    obj_parts = []
    if info['deps']:  # if had dependencies
        for type in info['deps']:
            if type != "case":  # ignore را
                for index in info['deps'][type]:
                    obj_parts.append((index, dependencyGraph.nodes[index]["word"]))
    obj_parts.append((info['address'], info['word']))
    obj_parts.sort(key=lambda a: a[0])
    if obj_parts:
        obj = " ".join([obj_part[1] for obj_part in obj_parts])
    else:
        obj = None
    return obj


def extract_verbs_from_dependency_graph(dependencyGraph, info):
    verb_parts = []
    if info['deps']:
        for type in info['deps']:
            if type == 'compound':
                for index in info['deps'][type]:
                    verb_parts.append(dependencyGraph.nodes[index]['word'])
    verb_parts.append(clean_verb(info['word']))
    return verb_parts


def create_dependency_graph(sentence):
    parser = DependencyParser(tagger=tagger, lemmatizer=lemmatizer)
    dependencyGraph = parser.parse(word_tokenize(sentence))
    subj = None
    obj = None
    verbs = []
    for i in range(len(dependencyGraph.nodes)):
        info = dependencyGraph.nodes[i]
        if info['tag'] == 'VERB':
            verbs.append(extract_verbs_from_dependency_graph(dependencyGraph, info))
        if info['rel'] == 'obj':
            obj = extract_obj_from_dependency_graph(dependencyGraph, info)
        if info['rel'] == 'nsubj':
            subj = extract_subj_from_dependency_graph(dependencyGraph, info)
    # print(dependencyGraph)
    return (subj, obj, verbs)


def remove_brackets(chunked_sent):
    return re.subn('_', ' ', re.subn(r'\[|]|[A-Z]', '', chunked_sent)[0])[0]


def main():
    normalizer = Normalizer()
    # text = input()
    text = "من دارم جبران می‌کنم."
    sentences = sent_tokenize(text)
    index_start_sentence = 0
    for sentence in sentences:
        normalized_sentence = normalizer.normalize(sentence)
        print("currently working on:", normalized_sentence)
        chunked_sub_sentences = chunk_sentence(normalized_sentence)
        for chunked_sub_sentence in chunked_sub_sentences:
            print("Chunker\n", chunked_sub_sentence)
            obj_from_chunker = extract_objects(chunked_sub_sentence) # list
            print("OBJs:", obj_from_chunker)
            verbs_from_chunker = extract_verb_phrases(chunked_sub_sentence) # list
            print("VERBS:", verbs_from_chunker)
            print("### ### ### ### ### ### ###\nDependency Parser ")
            subj_from_parser, obj_from_parser, verbs = create_dependency_graph(remove_brackets(chunked_sub_sentence))
            print("SUB:", subj_from_parser)
            print("OBJ:", obj_from_parser)
            print("VERBS", verbs)

        print("************************************************************************")
        index_start_sentence += len(sentence)

if __name__ == "__main__":
    main()
