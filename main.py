import popplerqt5
import sys
import PyQt5
import re
import csv
from datetime import date
import locale


def export_to_csv(counter,pdffilename,booktitle,time):
     with open('/home/zelenyeshtany/r.csv', 'w', newline='') as csvfile:
         today = date.today()
         spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
         spamwriter.writerow(today.strftime('%Y-%m-%d'), counter,time, booktitle, pdffilename,)
#         spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])


# returns TextBox object and its index within TextList
def getTextboxCoordsByHighlightCoords(page,highlight):
    pwidth = page.pageSize().width()
    pheight = page.pageSize().height()
    page_text = page.textList()
    textbox = None
    for i in range(len(page_text)):
        if(int(annot_get_x(highlight,pwidth))-1 <= int(page_text[i].boundingBox().x()) <= int(annot_get_x(highlight,pwidth))+1
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
    

def main():
    all_annots = []
    page_numbers = []
    filepath = "/home/zelenyeshtany/Books/10StepstoEarningAwesomeGrades.pdf"
    filename = filepath.split('/')[-1]
    doc = popplerqt5.Poppler.Document.load(filepath)
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
                    annotation.contents() == 'end')
                   ):
                    all_annots.append(annotation)
                    page_numbers.append(i)
    print('texts under highlights:')
    for i in range(len(all_annots)):
        print(my_annot_get_text(all_annots[i],doc.page(page_numbers[i])))
    print(' / texts under highlights:')
    # word counter
    print('all_annots : ' + str(len(all_annots)))
    print('page_numbers : ' + str(len(page_numbers)))
    word_count = 0
    last_start_page_number = page_numbers[len(all_annots)-2]
    last_end_page_number = page_numbers[len(all_annots)-1]
    last_start = all_annots[len(all_annots)-2]
    last_end = all_annots[len(all_annots)-1]
    
    # если есть промежуточные страницы
    print('last_end_page_number : '+str(last_end_page_number))
    print('last_start_page_number : ' + str(last_start_page_number))
    if(last_end_page_number - last_start_page_number > 0):
        # подсчет со start до конца страницы, если есть промежуточные страницы
        start_page = doc.page(last_start_page_number)
        start_page_text = start_page.textList()
        start_textbox = getTextboxCoordsByHighlightCoords(start_page,last_start)
        if(start_textbox):
            start_position = start_textbox[1]
        word_count += (len(start_page_text)-start_position)
        # / подсчет со start до конца страницы, если есть промежуточные страницы
    
        # подсчет слов на всех промежуточных страницах меджду end и start
        offset_page = last_start_page_number+1
        while(last_end_page_number - offset_page > 0):
            word_count+=len(doc.page(offset_page).textList())
            offset_page+=1
        # / подсчет слов на всех промежуточных страницах меджду end и start
       
        # подсчет с начала страницы end до самого end, если есть промежуточные страницы
        end_page = doc.page(last_end_page_number)
        end_textbox = getTextboxCoordsByHighlightCoords(end_page,last_end)
        if(end_textbox):
            end_position = end_textbox[1]
            word_count += end_position + 1
        # / подсчет с начала страницы end до самого end, если есть промежуточные страницы

    # если нет промежуточных страниц
    elif(last_end_page_number - last_start_page_number == 0):
        page_with_start_and_end = doc.page(last_start_page_number)

        start_textbox = getTextboxCoordsByHighlightCoords(page_with_start_and_end,last_start)
        if(start_textbox):
            start_position = start_textbox[1]

        end_textbox = getTextboxCoordsByHighlightCoords(page_with_start_and_end,last_end)
        if(end_textbox):
            end_position = end_textbox[1]
        word_count = end_position - start_position + 1
    print(word_count)
    print('modifdate:')
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
    print(last_start.modificationDate().toString())
    export_to_csv(word_count,filename,)
    return word_count
# / word counter
    
        
if __name__ == "__main__":
    main()
