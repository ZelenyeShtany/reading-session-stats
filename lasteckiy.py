import popplerqt5
import sys
import PyQt5
import re

def getTextboxCoordsByHighlightCoords(page,highlight):
    pwidth = page.pageSize().width()
    pheight = page.pageSize().height()
    page_text = page.textList()
    for i in range(len(page_text)):
        if(int(annot_get_x(highlight,pwidth))-1 <= int(page_textlist[i].boundingBox().x()) <= int(annot_get_x(highlight,pwidth))+1
           and
           int(annot_get_y(highlight,pheight))-1 <= int(page_textlist[i].boundingBox().y()) <= int(annot_get_y(highlight,pheight))+1
           ):
            return page_textlist[i]
    return None
        


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
    doc = popplerqt5.Poppler.Document.load("/home/zelenyeshtany/Books/10StepstoEarningAwesomeGrades.pdf")
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
    highlight_amender(all_annots,page_numbers,doc)
    # print('texts under highlights:')
#     for i in range(len(all_annots)):
#         print(my_annot_get_text(all_annots[i],doc.page(page_numbers[i])))
#     print(' / texts under highlights:')
#     # word counter
#     print('all_annots : ' + str(len(all_annots)))
#     print('page_numbers : ' + str(len(page_numbers)))
#     word_count = 0
#     last_start_page_number = page_numbers[len(all_annots)-2]
#     last_end_page_number = page_numbers[len(all_annots)-1]
#     last_start = all_annots[len(all_annots)-2]
#     last_end = all_annots[len(all_annots)-1]
    
#     # если есть промежуточные страницы
#     print('last_end_page_number : '+str(last_end_page_number))
#     print('last_start_page_number : ' + str(last_start_page_number))
#     if(last_end_page_number - last_start_page_number > 0):
#         # подсчет со start до конца страницы, если есть промежуточные страницы
#         start_page = doc.page(last_start_page_number)
#         start_page_width = start_page.pageSize().width()
#         start_page_height = start_page.pageSize().height()
#         start_page_text = start_page.textList()
#         #print('X:' + str(int(annot_get_x(last_start,start_page_width))))
#         #print('Y:' + str(int(annot_get_y(last_start,start_page_height))))
        
#         for i in range(len(start_page_text)):
#             #print(str(int(start_page_text[i].boundingBox().x())))
#             #print(str(int(start_page_text[i].boundingBox().y())))
#             if(int(annot_get_x(last_start,start_page_width))-1 <= int(start_page_text[i].boundingBox().x()) <= int(annot_get_x(last_start,start_page_width))+1
#                and
#                int(annot_get_y(last_start,start_page_height))-1 <= int(start_page_text[i].boundingBox().y()) <= int(annot_get_y(last_start,start_page_height))+1
#                ):
#                 start_position = i
#                 print('SRABOTALO')
#                 break
#         word_count += (len(start_page_text)-start_position)
#         # / подсчет со start до конца страницы, если есть промежуточные страницы
    
#         # подсчет слов на всех промежуточных страницах меджду end и start
#         offset_page = last_start_page_number+1
#         while(last_end_page_number - offset_page > 0):
#             word_count+=len(doc.page(offset_page).textList())
#             offset_page+=1
#         # / подсчет слов на всех промежуточных страницах меджду end и start
       
#         # подсчет с начала страницы end до самого end, если есть промежуточные страницы
#         end_page = doc.page(last_end_page_number)
#         end_page_width = end_page.pageSize().width()
#         end_page_height = end_page.pageSize().height()
#         end_page_text = end_page.textList()
#         for i in range(len(end_page_text)):
#             if((int(annot_get_x(last_end,end_page_width))-1 <= int(end_page_text[i].boundingBox().x()) <= int(annot_get_x(last_end,end_page_width))+1
#                 and
#                 int(annot_get_y(last_end,end_page_height))-1 <= int(end_page_text[i].boundingBox().y()) <= int(annot_get_y(last_end,end_page_height))+1
#                 )):
#                 end_position = i
#                 word_count += end_position + 1
#         # / подсчет с начала страницы end до самого end, если есть промежуточные страницы

#     # если нет промежуточных страниц
#     elif(last_end_page_number - last_start_page_number == 0):
#         page_with_start_and_end = doc.page(last_start_page_number)
#         (pwidth, pheight) = (page_with_start_and_end.pageSize().width(), page_with_start_and_end.pageSize().height())
#         page_text = page_with_start_and_end.textList()
#         for i in range(len(page_text)):
#             if(int(annot_get_x(last_start,pwidth))-1 <= int(page_text[i].boundingBox().x()) <= int(annot_get_x(last_start,pwidth))+1
#                and
#                int(annot_get_y(last_start,pheight))-1 <= int(page_text[i].boundingBox().y()) <= int(annot_get_y(last_start,pheight))+1
#                ):
#                 start_position = i
#             if(int(annot_get_x(last_end,pwidth))-1 <= int(page_text[i].boundingBox().x()) <= int(annot_get_x(last_end,pwidth))+1
#                and
#                int(annot_get_y(last_end,pheight))-1 <= int(page_text[i].boundingBox().y()) <= int(annot_get_y(last_end,pheight))+1
#                ):
#                 end_position = i
#         word_count = end_position - start_position + 1
#     print(word_count)
#     return word_count
# # / word counter
    
        
if __name__ == "__main__":
    main()
