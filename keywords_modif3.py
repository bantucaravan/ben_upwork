#!/usr/bin/env python
import sys 
import os
import re
import nltk
from tkinter import *
import random
import pdf2text_modif
import subprocess
import re
import io


nltk.download('averaged_perceptron_tagger')
#nltk.download('stopwords')
nltk.download('punkt')
#nltk.download('tagsets')

GUI = Tk()
GUI.title("Keyword Finder")

#open_text = Label(text = "Enter name of your PDF", fg = "black", bg = "white")
open_text = Label(text = "Choose PDF to Parse...", fg = "black", bg = "white")
open_text.pack()

top = Frame(GUI)
top.pack(side = TOP)

#entry = Entry(top)
#entry.pack()

# This function will extract and return the pdf file text content.
def run():
    # pdf location and file name
    pdf_path = filedialog.askopenfilename()
    #pdf_path = '/Users/admin/Desktop/Data Projects/Upwork/Alabama PDF/engines_of_creation2.pdf'
    

    # convert pdf to text
    # Very Slow
    # (1) subproccess approach
    # works on mac... issue with encoding of sys.stdout on windows
    #command = ['python', './pdf2text.py', pdf_path]
    #text = subprocess.check_output(command, shell=True)
    #text = text.decode(sys.stdout.encoding)
    #(2) python pdfminer approach
    print('Starting pdf to text conversion')
    text = pdf2text_modif.extract_text([pdf_path],outfile = 'string_buffer')
    print('End pdf to text conversion')

    # Clean and POS tag
    text = re.sub(r'-\n', '', text) # get rid of end of line dashes
    text = re.sub(r'\n\d*', ' ', text)
    #text.strip(u'\x0c') # handles in nltk.word_tokenize()    

    tokenize = nltk.word_tokenize
    #tokenize = nltk.tokenize.ToktokTokenizer().tokenize
    sents = nltk.sent_tokenize(text)
    # line below slow...
    # CPU times: user 12.3 s, sys: 225 ms, total: 12.5 s
    # Wall time: 12.6 s
    # is is POS or word tokenize, probs word tokenize bc regexs
    sents = [nltk.pos_tag(tokenize(sent)) for sent in sents]
    words, tags = zip(*[list(zip(*sent)) for sent in sents])

    # look at subordinating conjuctions and prepositions in
    #set(j[0] for i in sents for j in i if j[1] == 'IN')

    # Subordinating conjs list
    #sub_conjs = "After although before if since though unless until when whenever where whereas wherever whether while why, In order to, provided that, so that, rather than, even though, even if"
    #sub_conjs = sub_conjs.lower().split(',')
    #sub_conjs = sub_conjs[0].split() + sub_conjs[1:]
    #sub_conjs = [i.strip() for i in sub_conjs]
    #nots = '“as” “and” “that” than” “then”'
    #nots = [re.sub('[^a-zA-Z]', '', i) for i in nots.split()]
    #nots = ['as', 'and', 'that', 'than', 'then'] # final
    #sub_conjs = [i for i in sub_conjs if i not in nots]
    sub_conjs = ['after', 'although', 'before', 'if', 'since', 'though',
     'unless', 'until', 'when', 'whenever', 'where', 'whereas', 'wherever',
      'whether', 'while', 'why', 'in order to', 'provided that', 'so that',
       'rather than', 'even though', 'even if', 'rather', 'because']

    # create multi word expressions
    mwes = [tuple(i.split()) for i in sub_conjs if ' ' in i]
    multi_word = nltk.tokenize.MWETokenizer(mwes).tokenize
    sub_conj_mwes = [i.replace(' ', '_') for i in sub_conjs]

    detokenize = nltk.tokenize.treebank.TreebankWordDetokenizer().tokenize

    # Base Python Approach
    def check(words, tags):
        #words, tags = zip(*sent)
        noun = 0
        verb = 0
        sub_conj = 0
        for tag in tags:
            if tag.startswith('NN'):
                noun +=1
            if tag.startswith('VB'):
                verb +=1
        if set(sub_conj_mwes).intersection(multi_word(list(words))):
            sub_conj +=1

        res = (verb > 3) and bool(noun) and bool(sub_conj)
        if res:
            return words
        else: 
            return None

    # on engines_of_creation.pdf
    # CPU times: user 345 ms, sys: 6.39 ms, total: 351 ms
    # Wall time: 348 ms
    results = [(i, check(w, t)) for i, (w, t) in enumerate(zip(words, tags))]
    results = [i for i in results if i[1] != None]
    idxs, results = zip(*results)
    final_text = '\n\n'.join([detokenize(list(i)) for i in results])
    
    '''
    # Pandas approach
    import pandas as pd
    # there are some 'tags' that are commas??
    # A:punctuations gets tagged as itself
    tag_df = pd.DataFrame(list(tags))
    word_df = pd.DataFrame(list(words))

    def check_tag(row):
        noun = sum(row.dropna().str.startswith('NN'))
        verb = sum(row.dropna().str.startswith('VB'))
        res = bool(noun) and bool(verb)
        return res

    def check_word(row):
        words = row.dropna().tolist()
        res = set(sub_conj_mwes).intersection(multi_word(words))
        res = bool(res)
        return res

    mask = tag_df.apply(check_tag, axis=1)
    mask &= word_df.apply(check_word, axis=1)
    
    results = word_df.loc[mask,:].apply(lambda x: detokenize(x.dropna().tolist()), axis=1).values.tolist()
    #identical
    #results = word_df.loc[mask,:].values.tolist()
    #results = [detokenize([word for word in sent if word != None]) for sent in results]
    final_text = '\n\n'.join(results)
    '''


    textbox.delete(1.0, END)
    textbox.insert(END, final_text)
    textbox.config(state= DISABLED)
    textbox.pack(side = LEFT, fill = BOTH, expand=True)
    scroll.config(command=textbox.yview)

    basename = os.path.basename(pdf_path).split('.')[:-1]
    out_file = 'output_{}.txt'.format(basename)
    with open(out_file, 'wt', encoding= 'utf-8') as f:
        f.write(textbox.get(1.0, END))
    print('Done!')
    return

click_me = Button(top, text="Select File", command = run)
#click_me = Button(top, text="Submit", command = run)
click_me.place(x=215, y=60)
click_me.pack()

bottom = Frame(GUI)
bottom.pack()

scroll = Scrollbar(GUI)
scroll.pack(side=RIGHT, fill='y')

textbox = Text(GUI, width=60, yscrollcommand=scroll.set)

GUI.mainloop()









