import os
import shutil
import errno
import subprocess
import tempfile
from tempfile import mkdtemp
import re
import io

#############################
# 批量转换pdf 为txt 和 朗读语音MP3
# todo：转成MP3带歌词形式的 或者转成MP4带字幕的
#############################
import pyttsx3
engine = pyttsx3.init() # object creation

""" RATE"""
#engine.setProperty('rate', 300)     # setting up new voice rate 200是正常语速
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate

"""VOLUME"""
engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1
volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
print (volume)                          #printing current volume level

"""VOICE"""
voices = engine.getProperty('voices')       #getting details of current voice
engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male

engine.say("pdf转文字")
pyttsx3.speak('pdf转语音')

engine.say('My current speaking rate is ' + str(rate))
engine.runAndWait()

try:
    from PIL import Image
except ImportError:
    print('Error: You need to install the "Image" package. Type the following:')
    print('pip install Image')

try:
    import pytesseract
except ImportError:
    print('Error: You need to install the "pytesseract" package. Type the following:')
    print('pip install pytesseract')
    exit()

try:
    from pdf2image import convert_from_path, convert_from_bytes
except ImportError:
    print('Error: You need to install the "pdf2image" package. Type the following:')
    print('pip install pdf2image')
    exit()

import time
import sys
from textract import exceptions

def update_progress(progress):
    barLength = 10  # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format(
        "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
    print()


def run(args):
        # run a subprocess and put the stdout and stderr on the pipe object
        try:
            pipe = subprocess.Popen(
                args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        except OSError as e:
            if e.errno == errno.ENOENT:
                # File not found.
                # This is equivalent to getting exitcode 127 from sh
                raise exceptions.ShellError(
                    ' '.join(args), 127, '', '',
                )

        # pipe.wait() ends up hanging on large files. using
        # pipe.communicate appears to avoid this issue
        stdout, stderr = pipe.communicate()

        # if pipe is busted, raise an error (unlike Fabric)
        if pipe.returncode != 0:
            raise exceptions.ShellError(
                ' '.join(args), pipe.returncode, stdout, stderr,
            )

        return stdout, stderr


def extract_tesseract(filename):
        #temp_dir = mkdtemp()
        #base = os.path.join(temp_dir, 'conv')
        #temp_dir = 'tempdir'           
        temp_dir, _ = os.path.splitext(filename)
        contents = []
        
        try:
            import pymupdf
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                doc = pymupdf.open(filename) # open a document

                for page_index in range(len(doc)): # iterate over pdf pages
                    page = doc[page_index] # get the page
                    image_list = page.get_images()

                    # print the number of images found on the page
                    #if image_list:
                    #    print(f"Found {len(image_list)} images on page {page_index}")
                    #else:
                    #   print("No images found on page", page_index)

                    for image_index, img in enumerate(image_list, start=1): # enumerate the image list
                        xref = img[0] # get the XREF of the image
                        pix = pymupdf.Pixmap(doc, xref) # create a Pixmap

                        if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

                        pix.save("%s\\page_%05d-image_%02d.png" % (temp_dir, page_index, image_index)) # save the image as png
                        png_bytes = pix.tobytes()
                        page_content = pytesseract.image_to_string(Image.open(io.BytesIO(png_bytes)), 'eng+chi_sim')
                        contents.append(page_content)
                        pix = None
            else:
                for dirpath, dirnames, files in os.walk(temp_dir):
                    for name in files:
                        filename, file_extension = os.path.splitext(name)
                        if (file_extension.lower() != '.png'):
                            continue
                        source_path = os.path.join(dirpath, name)
                        relative_directory = os.path.dirname(os.path.realpath(name))
                        pngfile = os.path.join(relative_directory, source_path)
                        #print('pic path: ' + repr(pngfile))

                        page_content = pytesseract.image_to_string(Image.open(pngfile), 'eng+chi_sim')
                        contents.append(page_content)
            
            text = ''.join(contents)
            engine.save_to_file(text, temp_dir+'.mp3')
            engine.runAndWait()
            return text

            # https://python-pptx.readthedocs.io/en/latest/
            #stdout, _ = run(['pdftoppm', filename, base])
            print('extract_tesseract: ' + filename)
            for page in sorted(os.listdir(temp_dir)):
                page_path = os.path.join(temp_dir, page)
                # https://github.com/Belval/pdf2image
                page_content = pytesseract.image_to_string(Image.open(page_path))
                contents.append(page_content)
            return ''.join(contents)
        finally:
            #shutil.rmtree(temp_dir)
            pass

def convert_recursive(source, destination, count):
    pdfCounter = 0
    for dirpath, dirnames, files in os.walk(source):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdfCounter += 1
    print('pdfCounter: ' + str(pdfCounter))
    ''' Helper function for looping through files recursively '''
    for dirpath, dirnames, files in os.walk(source):
        for name in files:
            filename, file_extension = os.path.splitext(name)
            if (file_extension.lower() != '.pdf'):
                continue
            print('name:' + name)
            relative_directory = os.path.relpath(dirpath, source)
            source_path = os.path.join(dirpath, name)
            output_directory = os.path.join(destination, relative_directory)
            output_filename = os.path.join(output_directory, filename + '.txt')
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            count = convert(source_path, output_filename, count, pdfCounter)
    return count

def convert(sourcefile, destination_file, count, pdfCounter):
    if os.path.exists(destination_file):
        filename, file_extension = os.path.splitext(destination_file)
        with open(destination_file, 'r', newline='', encoding='utf-8') as txtfd:
            text = txtfd.read()
            #pyttsx3.speak(text)
            engine.save_to_file(text, filename+'.mp3')
            engine.runAndWait()
    else:
        text = extract_tesseract(sourcefile)
        with open(destination_file, 'w', encoding='utf-8') as f_out:
            f_out.write(text)
    print()
    print('Converted ' + source)
    count += 1
    update_progress(count / pdfCounter)
    return count

count = 0
print()
print('********************************')
print('*** PDF to TXT file, via OCR ***')
print('********************************')
print()
dir_path = os.path.dirname(os.path.realpath(__file__))
print('Source file or folder of PDF(s) [' + dir_path + ']:')
print('(Press [Enter] for current working directory)')
source = input()
if source == '':
    source = dir_path

print('Destination folder for TXT [' + dir_path + ']:')
print('(Press [Enter] for current working directory)')
destination = input()
if destination == '':
    destination = dir_path

if (os.path.exists(source)):
    if (os.path.isdir(source)):
        count = convert_recursive(source, destination, count)
    elif os.path.isfile(source):  
        filepath, fullfile = os.path.split(source)
        filename, file_extension = os.path.splitext(fullfile)
        if (file_extension.lower() == '.pdf'):
            count = convert(source, os.path.join(destination, filename + '.txt'), count, 1)
    plural = 's'
    if count == 1:
        plural = ''
    print(str(count) + ' file' + plural + ' converted')
else:
    print('The path ' + source + ' seems to be invalid')
