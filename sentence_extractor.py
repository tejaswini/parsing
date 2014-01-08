import pprint
import re

class ExtractSentences:
    def __init__(self, file_name):
        self.file_name = file_name
#        self.sentences = self.len_10_sentences()

    def lines(self):
        lines = []
        with open(self.file_name,"rb") as fp:
            lines = fp.readlines()
        return lines

    def len_10_sentences(self):
        sent_tags = []
        dependencies = []
        dependencies_index = []
        sub_sent = []
        for line in self.lines():
            if(line == "\n"):
                pos_tags, gold_dep, gold_dep_index,length = \
                    self.dependencies(sub_sent)
                sub_sent = []
                if(length <= 10):
                    sent_tags.append(pos_tags)
                    dependencies.append(gold_dep)
                    dependencies_index.append(gold_dep_index)
            else:
                sub_sent.append(line)
        return sent_tags,dependencies, dependencies_index

    def dependencies(self, sentence):
        pos_tags = []
        gold_dep_index = []
        gold_dep = ""

        for sent in sentence:
            comps = sent.split()
            gold_dep_index.append(comps[6])
            pos_tags.append(comps[3])

        pos_tags, gold_dep_index = \
            self.remove_punctuations(pos_tags, gold_dep_index, sentence)

        for index in gold_dep_index:
            if(index == "0"):
                gold_dep += " ROOT"
            else:
                gold_dep += " " + pos_tags[int(index)-1]
                
        return " ".join(pos_tags), gold_dep.strip(), \
               " ".join(gold_dep_index),len(pos_tags)

    def remove_punctuations(self, pos_tags, gold_dep_index, sentence):
        index_mapping = {0:0}
        i = 0
        blocked_tags = [",", ".", ":", "\'\'", "``", "(",")"]
        new_pos_tags = []
        new_gold_dep_index = []
        for index, tag in enumerate(pos_tags):
            if(tag not in blocked_tags):
                i += 1
                index_mapping[index+1] = i
                new_pos_tags.append(tag)
            else:
                index_mapping[index+1] = None
         
        for index, gold_index in enumerate(gold_dep_index):
            if(index_mapping[index+1]!=None and \
                   index_mapping[int(gold_index)]!=None):
                 new_gold_dep_index.\
                     append(str(index_mapping[int(gold_index)]))

        if len(new_gold_dep_index) != len(new_pos_tags):
            print " ".join(new_pos_tags)
            print " ".join(new_gold_dep_index)
            print  " ".join(pos_tags)
            print  " ".join(gold_dep_index)
            print(sentence)
            pprint.pprint(index_mapping)

        assert len(new_gold_dep_index) == len(new_pos_tags)

        return new_pos_tags, new_gold_dep_index
            
        

    def write_to_file(self, file_name, data):
        with open(file_name, "wb") as fp:
            fp.writelines(("%s\n" % line for line in data))
            
if __name__ == "__main__":
    extractor = ExtractSentences("data/wsj_sec_2_21_gold_dependencies")
    sentences, dependencies, dep_index = extractor.len_10_sentences()
    extractor.write_to_file("data/sample_sent.txt", sentences)
    extractor.write_to_file("data/sample_dep.txt", dependencies)
    extractor.write_to_file("data/sample_dep_index.txt", dep_index)
