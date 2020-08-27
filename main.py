#!/usr/bin/python
import popplerqt5
import sys
import PyQt5
import re
import csv
from datetime import datetime,date
import getopt
import os

def count_words_between_annotations(annot1,annot2,
                                    doc,annot1_page_number,
                                    annot2_page_number):
    word_count = 0
        # если есть промежуточные страницы
    if(annot2_page_number - annot1_page_number > 0):
        # подсчет со annot1 до конца страницы, если есть промежуточные страницы
        annot1_page = doc.page(annot1_page_number)
        annot1_page_text = annot1_page.textList()
        annot1_textbox = getTextboxCoordsByHighlightCoords(annot1_page,annot1)
        if(annot1_textbox):
            annot1_position = annot1_textbox[1]
        word_count += (len(annot1_page_text)-annot1_position)
        # / подсчет со annot1 до конца страницы, если есть промежуточные страницы
    
        # подсчет слов на всех промежуточных страницах меджду annot2 и annot1
        offset_page = annot1_page_number+1
        while(annot2_page_number - offset_page > 0):
            word_count+=len(doc.page(offset_page).textList())
            offset_page+=1
        # / подсчет слов на всех промежуточных страницах меджду annot2 и annot1
       
        # подсчет с начала страницы annot2 до самого annot2, если есть промежуточные страницы
        annot2_page = doc.page(annot2_page_number)
        annot2_textbox = getTextboxCoordsByHighlightCoords(annot2_page,annot2)
        if(annot2_textbox):
            annot2_position = annot2_textbox[1]
            word_count += annot2_position + 1
        # / подсчет с начала страницы annot2 до самого annot2, если есть промежуточные страницы

    # если нет промежуточных страниц
    elif(annot2_page_number - annot1_page_number == 0):
        page_with_annot1_and_annot2 = doc.page(annot1_page_number)

        annot1_textbox = getTextboxCoordsByHighlightCoords(page_with_annot1_and_annot2,annot1)
        if(annot1_textbox):
            annot1_position = annot1_textbox[1]

        annot2_textbox = getTextboxCoordsByHighlightCoords(page_with_annot1_and_annot2,annot2)
        if(annot2_textbox):
            annot2_position = annot2_textbox[1]
        word_count = annot2_position - annot1_position + 1
    return word_count
    #print(PyQt5.QtCore.QLocale.system().toString(last_start.modificationDate(),'yyyy-MM-dd HH:mm')) # raboraet = today,'yyyy-MM-dd HH:mm'


def export_to_csv(rows,csvfilename,exported_data_path):
    column_names = ['timestamp',
                    'amount_of_words',
                    'minutes spent',
                    'reading speed(words/minute)',
                    'start annotation position',
                    'end annotation position']
    try:
        csvfile = open(csvfilename, 'a', newline='')
    except:
        if not os.path.exists(exported_data_path):
            os.makedirs(exported_data_path)
        csvfile = open(csvfilename, 'w', newline='')
    if os.stat(csvfilename).st_size == 0: # if file is empty
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, lineterminator='\n')
        writer.writerow(column_names)
        csvfile.close()
    csvfile = open(csvfilename, 'a', newline='')
    
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, lineterminator='\n')

    writer.writerows(rows) # writerows
    report = 'wrote to file ' + '"' + csvfilename + '" ' + str(len(rows)) + ' rows'
    return report

# returns TextBox object and its index within TextList
def getTextboxCoordsByHighlightCoords(page,highlight):
    pwidth = page.pageSize().width()
    pheight = page.pageSize().height()
    page_text = page.textList()
    textbox = None
    for i in range(len(page_text)):
        # print('----')
        # print(annot_get_x(highlight,pwidth))
        # print('----')
        if(
                int(annot_get_x(highlight,pwidth))-1
           <= int(page_text[i].boundingBox().x())
           <= int(annot_get_x(highlight,pwidth))+1
           and
           int(annot_get_y(highlight,pheight))-1 <= int(page_text[i].boundingBox().y()) <= int(annot_get_y(highlight,pheight))+1
           ):
            textbox = [page_text[i],i]
    return textbox

def my_annot_get_text(annotation,page):
    quads = annotation.highlightQuads()
    pwidth = page.pageSize().width()
    pheight = page.pageSize().height()
    txt = ""
    for quad in quads:
        rect = (quad.points[0].x() * pwidth,
                quad.points[0].y() * pheight,
                quad.points[2].x() * pwidth,
                quad.points[2].y() * pheight)
    bdy = PyQt5.QtCore.QRectF()
    bdy.setCoords(*rect)
    txt = txt + page.text(bdy)
    return txt


def annot_get_x(annotation,pwidth):
    quads = annotation.highlightQuads()
    for quad in quads:
        x = (quad.points[0].x() * pwidth)
    return x

def annot_get_y(annotation,pheight):
    quads = annotation.highlightQuads()
    for quad in quads:
        y = (quad.points[0].y() * pheight)
    return y

def getClosestTextBoxAfterHighlight(page,highlight):
    pwidth = page.pageSize().width()
    pheight = page.pageSize().height()
    page_text = page.textList()
    allTextBoxesOnLine = []
    for i in range(len(page_text)):
        if(int(annot_get_y(highlight,pheight))-1 <= int(page_text[i].boundingBox().y()) <= int(annot_get_y(highlight,pheight))+1
           and
           page_text[i].boundingBox().x() > annot_get_x(highlight,pwidth)
           ):
            allTextBoxesOnLine.append(page_text[i])
    closestTextBox = allTextBoxesOnLine[0]
    for i in range(len(allTextBoxesOnLine)):
        if(page_text[i].boundingBox().x()-annot_get_x(highlight,pwidth)
        <
        closestTextBox.boundingBox().x()-annot_get_x(highlight,pwidth)):
           closestTextBox = page_text[i]
    return closestTextBox


def highlight_amender(all_annots,page_numbers,document):
    for i in range(len(all_annots)):
        cur_page = document.page(page_numbers[i])
        # есть ли пробельные символы в начале текста под хайлайтом
        annotation_text = my_annot_get_text(all_annots[i],cur_page)
        is_whitespaces_at_beginning = '^\s+'
        cur_page_text = cur_page.textList()
        cur_page_width = cur_page.pageSize().width()
        cur_page_height = cur_page.pageSize().height()
        # если есть, то исправить хайлайт под коорды текстбокса
        if(re.search(is_whitespaces_at_beginning, annotation_text) is not None):
            # найти коорды текстбокса
            closest_textbox = getClosestTextBoxAfterHighlight(cur_page,all_annots[i])
            # взять коорды этого текстбокса
            closest_textbox_x0 = closest_textbox.boundingBox().x()
            closest_textbox_y0 = closest_textbox.boundingBox().y()

#            print(closest_textbox.boundingBox().x())
            # исправить коорды хайлайта на корды текстбокса
            rect = (closest_textbox.boundingBox().x(),#/cur_page_width, # x0
                    closest_textbox.boundingBox().y(),#/cur_page_height, # y0
                    closest_textbox.boundingBox().width(), # x2 
                    closest_textbox.boundingBox().height() # y2
                    )
            PyQt5.QtCore.QList<Quad> quads
            for quad in quads:
                rect = (quad.points[0].x() * pwidth,
                        quad.points[0].y() * pheight,
                        quad.points[2].x() * pwidth,
                        quad.points[2].y() * pheight)
            all_annots[i].setHighlightQuads()

            rect1 = all_annots[i].boundary()
            print(rect1)
            rect2 = PyQt5.QtCore.QRectF(
                    closest_textbox.boundingBox().x()/cur_page_width, #x3
                    closest_textbox.boundingBox().y()/cur_page_height, #y3
                    closest_textbox.boundingBox().width()/cur_page_width, 
                    closest_textbox.boundingBox().height()/cur_page_height
                )
            print(rect2)
            #all_annots[i].setHighlightQuads()
            all_annots[i].setBoundary(
                PyQt5.QtCore.QRectF(
                    closest_textbox.boundingBox().x()/cur_page_width,#x3
                    closest_textbox.boundingBox().y()/cur_page_height,#y3
                    closest_textbox.boundingBox().width()/cur_page_width,
                    closest_textbox.boundingBox().height()/cur_page_height
                ))
            print(my_annot_get_text(all_annots[i],cur_page))
             # setboundary принимает QRectF с нормированными коордами
    converter = document.pdfConverter()
    converter.setOutputFileName("/home/zelenyeshtany/10.pdf")
    converter.setPDFOptions(popplerqt5.Poppler.PDFConverter.WithChanges) # save with changes (enumerator)
    converter.convert()    
    

def main(argv):
    
    
    #DEFAULTS
    archive_mode = True
    diff_mins = 0 # amount of time spent to reading
    timestamp = None # time when you was reading
    booksfolder = '/home/zelenyeshtany/Books'
    pdffilenames = ['/10StepstoEarningAwesomeGrades.pdf','/Metascript-Method-v1.pdf']
    exported_data_path = '/home/zelenyeshtany/Sync/tables/reading-session-stats-data/books'
    #/DEFAULTS
    
    #OPTIONS
    try:
        opts, args = getopt.getopt(argv,"A:hf:m:t:",["archive-off","help","mins=","timestamp="])
    except getopt.GetoptError:
        print('error, see --help')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h","--help"):
            print('usage: ' + os.path.basename(__file__)+' [OPTIONS]')
            print('OPTIONS:')
            print('-A, --archive-off\tturns off archive mode and tries to export all the data from given file')
            print('-h, --help\treturns help info')
            print('-m, --mins\tspecifies amount of time spent to reading (in minutes).')
            print('\t\tDefault: last_start_annot.lastModifiedTime() - last_end_annot.lastModifiedTime()')
            print('-t, --timestamp\tSpecifies time when you was reading')
            sys.exit()
        elif opt in ("-t", "--timestamp"):
            timestamp = arg
        elif opt in ("-A", "--archive-off"):
            archive_mode = False
        elif opt in ("-m", "--mins"):
            diff_mins = arg
    #/OPTIONS


    for pdffilename in pdffilenames:
        all_annots = [] # all 'start' and 'end' annotations (which contents is either 'start' or 'end')
        all_ends = []
        all_starts = []
        page_numbers = [] # all_annots[5] returns HighlightAnnotation object and page_numbers[5] returns number of page in which this annotations resides
        end_page_numbers = []
        start_page_numbers = []

        csvfilename = exported_data_path + re.search('(.+?)(\.pdf)',pdffilename).group(1) + '.csv'    
        doc = popplerqt5.Poppler.Document.load(booksfolder + pdffilename)

        if(doc is None):
             print('Document not found')
             return 'Document not found'
        starts_counter = 0 # how many 'start' annotations exist in this file
        ends_counter = 0 # how many 'end' annotations exist in this file
    
        # start/end count
        for i in range(doc.numPages()):
            page = doc.page(i)
            (pwidth, pheight) = (page.pageSize().width(), page.pageSize().height())
            annotations = page.annotations()
            if len(annotations) > 0:
                for annotation in annotations:
                    if(isinstance(annotation, popplerqt5.Poppler.HighlightAnnotation)
                       and
                       (annotation.contents() == 'start'
                        or
                        re.search('(end)([ ]+\d+)?',annotation.contents())
                       )):
                        if 'end' in (annotation.contents()):
                            ends_counter+=1
                            all_ends.append(annotation)
                            end_page_numbers.append(i)
                        else:
                            starts_counter+=1
                            all_starts.append(annotation)
                            start_page_numbers.append(i)
                        all_annots.append(annotation)
                        page_numbers.append(i)
        #/ start/end count
    
        # cheching for errors
        if(starts_counter!=ends_counter):
            print('Error: "start" annotations:'+str(starts_counter)+', "end" annotations:'+str(ends_counter))
            if(starts_counter>ends_counter):
                print('Add another "end" annotation after last "start" annotation')
            else:
                print('Add another "start" annotation before last "end" annotation')
        # /cheching for errors
    
        # import all the data from csv file
        datafromcsvfile = []
        try:
            csvfile = open(csvfilename, 'r')
        except:
            if not os.path.exists(exported_data_path):
                os.makedirs(exported_data_path)
            csvfile = open(csvfilename, 'w')
            csvfile.close()
            csvfile = open(csvfilename, 'r')
        csvreader = csv.reader(csvfile, quoting=csv.QUOTE_ALL, lineterminator='\n')
        rowiter = 0
        for row in csvreader:
            if rowiter==0: # skip the first row which contains column names
                rowiter+=1
                continue
            datafromcsvfile.append([row[4], # start anniotation position(page and coords within this page)
                                    row[5]])# end anniotation position(page and coords within this page)
            rowiter+=1
        csvfile.close()
        # /import all the data from csv file
    
        # append to  rowstoexport only those rows that havent been exported to csv file
        rowstoexport = []
        for i in range(len(all_starts)): # or all_ends, not a big deal
            end_page = doc.page(end_page_numbers[i])
            end_page_width = end_page.pageSize().width()
            end_page_height = end_page.pageSize().height()
            not_found = 1
    
            # specifying timestamp (first column in the csv file)
            timestamp = all_starts[i].modificationDate().toPyDateTime()
            for j in range(len(datafromcsvfile)):
                if(str(end_page_numbers[i]) ==
                   datafromcsvfile[j][1].split(':')[0]
                   and
                   str(round(annot_get_x(all_ends[i],end_page_width),3)) == datafromcsvfile[j][1].split(':')[1] # float or int
                   and
                   str(round(annot_get_y(all_ends[i],end_page_height),3)) == datafromcsvfile[j][1].split(':')[2] # float or int
                   ):
                    not_found = 0
                    break
            if not_found:
                # specifying reading session duration
                if(diff_mins == 0):
                    if len(all_ends[i].contents().split(' ')) == 2:
                        diff_mins = int(all_ends[i].contents().split(' ')[1])
                    else:
                        diff_mins = 0
                # /specifying reading session duration
    
                word_count = count_words_between_annotations(
                    all_starts[i],
                    all_ends[i],
                    doc,
                    end_page_numbers[i],
                    start_page_numbers[i]
                )
    
                if int(diff_mins):
                    reading_speed = round(word_count/int(diff_mins),2)
                else:
                    reading_speed = word_count
    
                start_page = doc.page(start_page_numbers[i])
                start_page_width = start_page.pageSize().width()
                start_page_height = start_page.pageSize().height()
                
                start_position = str(start_page_numbers[i]) + ':' + str(round(annot_get_x(all_starts[i],start_page_width),3)) + ':' + str(round(annot_get_y(all_starts[i],start_page_height),3))
                end_position = str(end_page_numbers[i]) + ':' + str(round(annot_get_x(all_ends[i],end_page_width),3)) + ':' + str(round(annot_get_y(all_ends[i],end_page_height),3))
                
                row = [timestamp.strftime('%Y-%m-%d %H:%M'),
                    word_count,
                    diff_mins,
                    reading_speed,
                    start_position,
                    end_position]
                rowstoexport.append(row)
                
        # /append to  rowstoexport only those rows that havent been exported to csv file
                       
        print(export_to_csv(rowstoexport,csvfilename,exported_data_path))
    return 1
    
        
if __name__ == "__main__":
    main(sys.argv[1:])
