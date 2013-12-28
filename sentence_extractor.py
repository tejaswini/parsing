import pprint
import re

class ExtractSentences:
    def __init__(self, file_name):
        self.file_name = file_name
        self.sentences = self.len_15_sentences()

    def lines(self):
        lines = []
        with open(self.file_name,"rb") as fp:
            lines = fp.readlines()
        return lines

    def len_15_sentences(self):
        sent_tags = []
        dependencies = []
        dependencies_index = []
        sub_sent = []
        for line in self.lines():
            if(line == "\n"):
                if(len(sub_sent) <= 10):
                    pos_tags, gold_dep, gold_dep_index = \
                        self.dependencies(sub_sent)
                    sent_tags.append(pos_tags)
                    dependencies.append(gold_dep)
                    dependencies_index.append(gold_dep_index)
                sub_sent = []
            else:
                sub_sent.append(line)
        return sent_tags,dependencies, dependencies_index

    def dependencies(self, sentence):
        all_tags = []
        pos_tags = []
        gold_dep_index = []
        gold_dep = ""
        for sent in sentence:
            comps = sent.split()
            all_tags.append(comps[3])
#            if(re.match('^[a-zA-Z]+\.*$', comps[1])):
            gold_dep_index.append(comps[6])
            pos_tags.append(comps[3])

        for index in gold_dep_index:
            if(index == "0"):
                gold_dep += " ROOT"
            else:
                gold_dep += " " + all_tags[int(index)-1]
                
        return " ".join(pos_tags), gold_dep.strip(), \
               " ".join(gold_dep_index)

    def write_to_file(self, file_name, data):
        with open(file_name, "wb") as fp:
            fp.writelines(("%s\n" % line for line in data))
            
if __name__ == "__main__":
    extractor = ExtractSentences("wsj_sec_2_21_gold_dependencies")
    sentences, dependencies, dep_index = extractor.len_15_sentences()
    extractor.write_to_file("sentences_all.txt", sentences)
    extractor.write_to_file("dep_all.txt", dependencies)
    extractor.write_to_file("dep_index_all.txt", dep_index)
