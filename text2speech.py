
import pyttsx3

import sys, pathlib, pymupdf
import os
#fname = sys.argv[1]  # get document filename
fname = '啊哈！算法.pdf_tmp.pdf_tmp.pdf'  # get document filename

engine = pyttsx3.init() # object creation

""" RATE"""
engine.setProperty('rate', 300)     # setting up new voice rate 200是正常语速
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate

"""VOLUME"""
engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1
volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
print (volume)                          #printing current volume level

"""VOICE"""
voices = engine.getProperty('voices')       #getting details of current voice
engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male 中文 女
#engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female 日语 女
#engine.setProperty('voice', voices[2].id)   #changing index, changes voices. 1 for female 英文 女
print(len(voices))

engine.say("文字转语音")
engine.say('My current speaking rate is ' + str(rate))
engine.runAndWait()
#engine.stop()


"""Saving Voice to a file"""
# On linux make sure that 'espeak' and 'ffmpeg' are installed
#engine.save_to_file('Hello World', 'test.mp3')
#engine.runAndWait()

temp_dir = '.'
for dirpath, dirnames, files in os.walk(temp_dir):
    for name in files:
        filename, file_extension = os.path.splitext(name)
        if (file_extension.lower() != '.txt' or filename == 'requirements.txt'):
            continue    
        with open(name, 'r', newline='', encoding='utf-8') as txtfd:
            text = txtfd.read()
            #pyttsx3.speak(text)
            engine.save_to_file(text, filename+'.mp3')
            engine.runAndWait()

print("文字转语音")

def llll():
    with pymupdf.open(fname) as doc:  # open document
        text = chr(12).join([page.get_text() for page in doc])
        # write as a binary file to support non-ASCII characters
        pathlib.Path(fname + ".txt").write_bytes(text.encode())
        #pyttsx3.speak(text)

def lll():
    doc = pymupdf.open("啊哈！算法.pdf_tmp.pdf_tmp.pdf")
    header = "Header"  # text in header
    footer = "Page %i of %i"  # text in footer
    for page in doc:
        if page.number < 30:
            continue
        page.insert_text((50, 50), header)  # insert header
        page.insert_text(  # insert footer 50 points above page bottom
            (50, page.rect.height - 50),
            footer % (page.number + 1, doc.page_count),
        )
        # 提取文字
        text = page.get_text()
        print(text)
        pyttsx3.speak(text)
