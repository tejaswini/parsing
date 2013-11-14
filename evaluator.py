import pprint

class Evaluator:
    def __init__(self,file_name):
        self.file_name = file_name
        self.sentences = self.len_15_sentences()

    def lines(self):
        lines = []
        with open(self.file_name,"rb") as fp:
            lines = fp.readlines()
        return lines

    def len_15_sentences(self):
        sentences = []
        sub_sentence = []
        for line in self.lines():
            if(line == "\n"):
                if(len(sub_sentence) <= 12):
                       self.get_tags(sub_sentence)
                sub_sentence = []
            else:
                sub_sentence.append(line)

    def get_tags(self,sentence):
        tags = []
        gold_tag_index = []
        gold_tags = []
        for sent in sentence:
            comps = sent.split()
            tags.append(comps[3])
            gold_tag_index.append(comps[6])

        for index in gold_tag_index:
            if(index == "0"):
                gold_tags.append(None)
            else:
                gold_tags.append(tags[int(index)-1])
        pprint.pprint(gold_tags)
        pprint.pprint(gold_tag_index)
        return tags,gold_tags,gold_tag_index

            
if __name__ == "__main__":
#    evaluator = Evaluator("wsj_sec_2_21_gold_dependencies")
    evaluator = Evaluator("sample_text")
    evaluator.len_15_sentences()
